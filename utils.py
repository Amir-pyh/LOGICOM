import json
from type import ModelType, AgentType
import tkinter as tk
import pandas as pd
import os
import html
import shutil

def replace_variables(text, variables):
    for variable, value in variables.items():
        text = text.replace(variable, str(value))
    return text


def extract_prompt(file_path, variables):
    with open(file_path, 'r') as file:
        content = file.read()

    system_start_marker = "==== SYSTEM ===="
    user_start_marker = "==== ASSISTANT ===="

    system_start = content.find(system_start_marker) + len(system_start_marker)
    system_end = content.find(user_start_marker)
    system_text = content[system_start:system_end].strip()

    user_start = content.find(user_start_marker) + len(user_start_marker)
    assistant_text = content[user_start:].strip()

    system_text = replace_variables(system_text, variables)
    assistant_text = replace_variables(assistant_text, variables)

    return system_text, assistant_text


def save_xlsx(memory_log_path, topic_id, chat_id, helper_type, result, number_of_rounds,claim):

    memory_log_path_xlsx = os.path.join(memory_log_path, "all.xlsx")

    if os.path.exists(memory_log_path_xlsx):
        df = pd.read_excel(memory_log_path_xlsx)
        if topic_id in df["Topic_ID"].values:
            df.loc[df["Topic_ID"] == topic_id, helper_type] = result
            df.loc[df["Topic_ID"] == topic_id, f'{helper_type}_Round'] = number_of_rounds
            df.loc[df["Topic_ID"] == topic_id, f'Chat_ID_{helper_type}'] = str(chat_id)

        else:
            new_row = pd.DataFrame([[topic_id, claim, result, number_of_rounds, str(chat_id)]],
                                   columns=["Topic_ID", "claim", f'{helper_type}', f'{helper_type}_Round',
                                            f'Chat_ID_{helper_type}'])
            df = pd.concat([df, new_row], ignore_index=True)

    else:
        df = pd.DataFrame(columns=["Topic_ID","claim",  "No_Helper", "Vanilla_Helper", "Fallacy_Helper", "No_Helper_Round",
                                   "Vanilla_Helper_Round", "Fallacy_Helper_Round", "Chat_ID_No_Helper",
                                   "Chat_ID_Vanilla_Helper", "Chat_ID_Fallacy_Helper"])

        # Append a new row to the DataFrame
        new_row = pd.DataFrame([[topic_id, claim, result, number_of_rounds,str(chat_id)]],
                               columns=["Topic_ID","claim", f'{helper_type}', f'{helper_type}_Round', f'Chat_ID_{helper_type}'])

        df = pd.concat([df, new_row], ignore_index=True)

    # Save the DataFrame to the Excel file using XlsxWriter as the engine
    writer = pd.ExcelWriter(memory_log_path_xlsx, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    writer.close()



def save_jason(memory_log,memory_log_path, topic_id, chat_id, helper_type, result,
             number_of_rounds,finish_reason):

    memory_log_path_json = os.path.join(memory_log_path, topic_id, helper_type, f"{chat_id}.json")
    data = {"Topic_ID": topic_id,
            "log": memory_log.chat_memory.log[0].inputs,
            "chat_id": chat_id,
            "number_of_rounds":number_of_rounds,
            "Stop_reason": finish_reason,
            "Convinced?": result,
           }
    with open(memory_log_path_json, "w") as json_file:
        json.dump(data, json_file)





def save_html(memory_log, memory_log_path, topic_id, chat_id, helper_type, result,
              number_of_rounds,finish_reason):
    """
    Save log files in HTML format.
    """
    # Define color codes
    colors = ['blue', 'green']  # Blue and green colors
    round_number_color = 'red'

    # Generate the HTML content
    html_content = '<html><head><style>'
    html_content += 'body { font-family: Arial, sans-serif; }'
    html_content += '.log-container { width: 80%; margin: 0 auto; word-wrap: break-word; white-space: pre-wrap; }'
    html_content += f'.round-number {{ color: {round_number_color}; font-weight: bold; }}'
    html_content += f'.log-entry {{ font-weight: bold; }}'
    html_content += '</style></head><body>'

    html_content += '<div class="log-container">'

    for i, item in enumerate(memory_log.chat_memory.log[0].inputs):
        color = colors[i % len(colors)]
        additional_string = 'Convincing_AI: ' if i % 2 == 0 else 'Debater_Agent:'

        # Calculate the rounded number
        round_number = (i // 2) + 1

        log_text = list(item.values())[0]

        # Escape special characters for HTML display
        log_text = html.escape(log_text)

        html_content += f'<div class="round-number">{round_number}.</div>'
        html_content += f'<div class="log-entry" style="color:{color};">{additional_string}{log_text}</div>'
        html_content += '<br>'

    html_content += '</div>'  # Close the log-container div

    # Add result and number of rounds at the end of the file
    html_content += '<br>'
    html_content += f'<div class="log-entry"><b>Result:</b> {result}</div>'
    html_content += f'<div class="log-entry"><b>Stop Reason:</b> {finish_reason}</div>'
    html_content += f'<div class="log-entry"><b>Number of Rounds:</b> {number_of_rounds}</div>'

    html_content += '</body></html>'

    memory_log_path_html = os.path.join(memory_log_path, topic_id, helper_type, f"{chat_id}.html")
    with open(memory_log_path_html, 'w') as file:
        file.write(html_content)

def save_txt(memory_log,memory_log_path, topic_id, chat_id, helper_type, result,
             number_of_rounds,finish_reason):
    """
    Save log files in txt format. Agent responses.
    """
    json_data = json.dumps(memory_log.chat_memory.log[0].inputs)
    memory_log_path_txt=os.path.join(memory_log_path, topic_id, helper_type, f"{chat_id}.txt")
    with open(memory_log_path_txt, 'w') as file:
        file.write(json_data)


def create_directory(directory_path):
    if os.path.exists(directory_path):
        # Directory exists, so remove it
        try:
            shutil.rmtree(directory_path)
            print(f"Directory '{directory_path}' removed successfully.")
        except OSError as e:
            print(f"Error occurred while removing directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' does not exist.")

    # Create the new directory
    try:
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")
    except OSError as e:
        print(f"Error occurred while creating directory '{directory_path}': {e}")
def save_log(memory_log, memory_log_path, topic_id, chat_id, result, helper, number_of_rounds,claim, finish_reason):
    """
    Save log files in both HTML and txt formats.
    """
    create_directory(os.path.join(memory_log_path, topic_id, helper))
    save_jason(memory_log=memory_log,memory_log_path=memory_log_path, topic_id=topic_id, chat_id=chat_id, helper_type=helper, result=result,
             number_of_rounds=number_of_rounds,finish_reason=finish_reason)
    save_html(memory_log=memory_log,memory_log_path=memory_log_path, topic_id=topic_id, chat_id=chat_id, helper_type=helper, result=result,
             number_of_rounds=number_of_rounds,finish_reason=finish_reason)
    save_txt(memory_log=memory_log,memory_log_path=memory_log_path, topic_id=topic_id, chat_id=chat_id, helper_type=helper, result=result,
             number_of_rounds=number_of_rounds,finish_reason=finish_reason)
    save_xlsx(memory_log_path=memory_log_path, topic_id=topic_id, chat_id=chat_id, helper_type=helper, result=result,
             number_of_rounds=number_of_rounds, claim=claim, )


r''' Save the generated fallacy. The file address should be changed manually.  '''


def save_fallacy(topic_id, chat_id, argument, counter_argument, fallacy, fallacious_argument=None):

    path = 'path/to/save/fallacies/'
    df = pd.read_csv(path)
    if not fallacious_argument:
        fallacious_argument = ''

    new_row = pd.DataFrame([[topic_id, chat_id, argument, counter_argument, fallacy,fallacious_argument]],
                           columns=["Topic_ID", "Chat_ID", "Argument", "Counter_Argument", "Fallacy", 'Fallacious_Argument'])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)


def get_variables(data, agent_type, dataset_type=None):

    # Handling for different agent types
    if agent_type == AgentType.DEBATER_AGENT:
        return {
            "<TOPIC>": str(data['title']),
            "<CLAIM>": str(data['claim']),
            "<ORIGINAL_TEXT>": str(data['original_text']),
            "<REASON>": str(data['reason']),
            "<WARRANT_ONE>": str(data['warrant_one']),
            "<WARRANT_TWO>": str(data['warrant_two']),
            "<SIDE>": "ONE",
            "<O-SIDE>": "TWO"
        }
    elif agent_type == AgentType.PERSUADER_AGENT:
        return {
            "<TOPIC>": str(data['title']),
            "<CLAIM>": str(data['claim']),
            "<ORIGINAL_TEXT>": str(data['original_text']),
            "<REASON>": str(data['reason']),
            "<WARRANT_ONE>": str(data['warrant_one']),
            "<WARRANT_TWO>": str(data['warrant_two']),
            "<SIDE>": "TWO",
            "<O-SIDE>": "ONE"
        }


r''' This is for human persuader-test'''


class ChatWindow:
    def __init__(self, on_submit):
        self.window = tk.Tk()
        self.input_text = tk.StringVar()
        self.chat_text = tk.StringVar()
        self.on_submit = on_submit
        self.is_running = True

        self.window.title("Chatbot")
        self.window.geometry("1800x1600")

        chat_frame = tk.Frame(self.window, relief=tk.SUNKEN, bd=2)
        chat_frame.pack(pady=100, expand=True, fill=tk.BOTH)

        chat_scrollbar = tk.Scrollbar(chat_frame)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        chat_view = tk.Text(chat_frame, yscrollcommand=chat_scrollbar.set)
        chat_view.pack(expand=True, fill=tk.BOTH)
        chat_scrollbar.config(command=chat_view.yview)

        input_frame = tk.Frame(self.window)
        input_frame.pack(pady=10)

        input_entry = tk.Entry(input_frame, textvariable=self.input_text)
        input_entry.pack(side=tk.LEFT)

        submit_button = tk.Button(input_frame, text="Submit", command=self.submit)
        submit_button.pack(side=tk.LEFT)

        break_button = tk.Button(input_frame, text="Break", command=self.break_loop)
        break_button.pack(side=tk.LEFT)

        self.chat_view = chat_view
        chat_view.tag_configure("bot", foreground="red")

        self.input_entry = input_entry  # Save the input entry reference
        self.window.mainloop()

    def submit(self):
        user_input = self.input_text.get()
        self.on_submit(user_input, self)
        self.input_text.set("")

    def break_loop(self):
        self.is_running = False
        self.window.destroy()

    def resize_input_entry(self, event):
        text = self.input_entry.get()
        width = len(text) + 1  # Calculate the new width based on the input text
        self.input_entry.config(width=width)

