import time
import openai

from tqdm import tqdm
import google.generativeai as palm
from agents.modertorAgent import ModeratorAgent
from config.gptconfig import ChatGPTConfig

from utils import *
import argparse
from agents.persuaderAgent import PersuaderAgent
from agents.debaterAgent import DebaterAgent
from colorama import init, Fore, Back, Style

import uuid

init()


def define_arguments():
    parser = argparse.ArgumentParser(description="Your script description here")

    parser.add_argument("--api_key_openai", required=True, help="API key for openAI")
    parser.add_argument("--api_key_palm", required=True, help="API key for PaLM")
    parser.add_argument("--claim_number", default=1, help="The claim number in dataset")
    parser.add_argument("--persuader_instruction", default='persuader_claim_reason_instruction',
                        help="Instruction for persuader")
    parser.add_argument("--debater_instruction", default='debater_claim_reason_instruction',
                        help="Instruction for debater")
    parser.add_argument("--helper_prompt_instruction", default='No_Helper', help="Instruction for Helper")
    parser.add_argument("--data_path", default='./claims/all-claim-not-claim.csv', help="Path to the source data")
    parser.add_argument("--log_html_path", default='./debates/', help="Path to save the debates")

    args = parser.parse_args()

    args.moderator_terminator_instruction_palm = 'moderator_terminator_instruction'
    args.moderator_tag_checker_instruction_palm = 'moderator_TagChecker_instruction'
    args.moderator_topic_checker_instruction_palm = 'moderator_topic_instruction'
    args.moderator_terminator_instruction_gpt = 'moderator_terminator_instruction'
    args.moderator_tag_checker_instruction_gpt = 'moderator_TagChecker_instruction'
    args.moderator_topic_checker_instruction_gpt = 'moderator_topic_instruction'
    args.memory_instruction = 'summary_instruction'

    return args


def run(persuader_agent, debater_agent, moderator_agent_1, moderator_agent_2, moderator_agent_3, moderator_agent_4,
        moderator_agent_5, args, topic_id, chat_id, claim, gpt4_moderator):
    print(arg.log_html_path)
    human = False
    keep_talking = True
    round_of_conversation: int = 1
    if gpt4_moderator:
        print(Fore.RED + '\n ****** GPT-4_MODERATOR *******' + Style.RESET_ALL)
    else:
        print(Fore.GREEN + '\n ****** PaLM_MODERATOR *******' + Style.RESET_ALL)
    print(Fore.RED + '\n ******************************* TOPIC******************' + Style.RESET_ALL)
    print(Fore.RED + '******************************* TOPIC******************' + Style.RESET_ALL)
    print(Fore.RED + '******************************* TOPIC******************' + Style.RESET_ALL)
    print(persuader_agent.last_response)

    if human:
        def handle_submit(user_input, window):
            debater_response_to_human = debater_agent.call(user_input)
            window.chat_view.insert(tk.END, "You: {}\n".format(user_input))
            window.chat_view.insert(tk.END, "\n")
            window.chat_view.insert(tk.END, "-" * 30 + "\n", "line")
            window.chat_view.insert(tk.END, "Debater: {}\n".format(debater_response_to_human))
            window.chat_view.insert(tk.END, "\n")
            window.chat_view.see(tk.END)

            if not window.is_running:
                window.window.destroy()

        chat_window = ChatWindow(on_submit=handle_submit)
        chat_window.insert(tk.END, "You: {}\n".format('test'))
        chat_window.see(tk.END)
    else:

        while keep_talking:
            finish_reason = None
            result = None

            r"""debater"""
            print(Fore.MAGENTA + 'round_of_conversation:' + str(round_of_conversation) + Style.RESET_ALL)
            print(Fore.GREEN + "\033[3m ********Agent2*************.\033[0m " + Style.RESET_ALL)
            print(Fore.GREEN + "********Debater*************" + Style.RESET_ALL)
            debater_response = debater_agent.call(persuader_agent.last_response)
            print(debater_response)

            r"""persuader"""
            print(Fore.BLUE + "\033[3m ********Agent1*************.\033[0m " + Style.RESET_ALL)
            print(Fore.BLUE + "********Persuader*************" + Style.RESET_ALL)
            if persuader_agent.helper_feedback_switch:
                persuader_response, fallacy, fallacious_argument = persuader_agent.call(debater_agent.last_response)
            else:
                persuader_response, fallacy = persuader_agent.call(debater_agent.last_response)
                fallacious_argument = None
            print(persuader_response)

            r'''**********Moderator*********'''
            print(Fore.RED + "******** MODERATOR *************" + Style.RESET_ALL)
            # This is used for topics that PaLM sends None.
            if gpt4_moderator:
                print(Fore.RED + '\n ****** GPT-4_MODERATOR *******' + Style.RESET_ALL)
                # GPT 4 Moderator
                moderator_command_4 = moderator_agent_4.call(persuader_agent.memory.chat_memory.log[0].inputs)
                # GPT 3 MODERATOR
                # moderator_command_5 = moderator_agent_5.call(persuader_agent.memory.chat_memory.log[0].inputs)
                print(moderator_command_4.info.value)
                if moderator_command_4.result:
                    result = True
                else:
                    result = False
                if moderator_command_4.terminate:
                    finish_reason = str(moderator_command_4.info.value)
                    break
                time.sleep(40)
            else:

                moderator_command_1 = moderator_agent_1.call(persuader_agent.memory.chat_memory.log[0].inputs)

                if moderator_command_1 == None:
                    print(
                        Fore.RED + '\n ****** Replacing PaLM moderator with GPT-4_MODERATOR *******' + Style.RESET_ALL)
                    moderator_command_4 = moderator_agent_4.call(persuader_agent.memory.chat_memory.log[0].inputs)
                    # GPT 3 MODERATOR
                    #  moderator_command_5 = moderator_agent_5.call(persuader_agent.memory.chat_memory.log[0].inputs)
                    print(moderator_command_4.info.value)
                    if moderator_command_4.result:
                        result = True
                    else:
                        result = False
                    if moderator_command_4.terminate:
                        finish_reason = str(moderator_command_4.info.value)
                        break

                    time.sleep(35)
                    gpt4_moderator = True
                    continue
                moderator_command_2 = moderator_agent_2.call(persuader_agent.memory.chat_memory.log[0].inputs)
                moderator_command_3 = moderator_agent_3.call(persuader_agent.memory.chat_memory.log[0].inputs)

                print(moderator_command_1.info.value)
                print(moderator_command_2.info.value)
                print(moderator_command_3.info.value)

                if moderator_command_1.result and moderator_command_2.result and moderator_command_3.result:
                    result = True
                else:
                    result = False

                if moderator_command_1.terminate and moderator_command_2.terminate and moderator_command_3.terminate:
                    finish_reason = str(moderator_command_1.info.value)
                    break

            round_of_conversation += 1
            if int(round_of_conversation) > 12:
                print("safety stop")
                break

            time.sleep(1)

    print(Fore.RED + "******** Conversation Result *************" + Style.RESET_ALL)
    print(result)

    r"""Number of token used """
    print("persuader used token: ", int(persuader_agent.model_backbone.token_used)
          + int(persuader_agent.model_backbone_helper.token_used) +
          int(persuader_agent.memory.model_backbone.token_used))
    print("Debater used token: ", int(debater_agent.model_backbone.token_used)
          +
          int(debater_agent.memory.model_backbone.token_used)
          )
    print("Number of token used for this conversation: ",
          int(debater_agent.model_backbone.token_used)
          + int(persuader_agent.model_backbone.token_used) +
          int(persuader_agent.model_backbone_helper.token_used) +
          int(debater_agent.memory.model_backbone.token_used) +
          int(persuader_agent.memory.model_backbone.token_used)
          )
    if gpt4_moderator:
        print("Number of token each moderator used", moderator_agent_4.model_backbone.token_used)
    else:
        print("Number of token each moderator used", moderator_agent_1.model_backbone.token_used)

    r"""Save the log"""
    save_log(memory_log=persuader_agent.memory,
             memory_log_path=args.log_html_path,
             topic_id=topic_id,
             chat_id=chat_id,
             result=result,
             helper=args.helper_prompt_instruction,
             number_of_rounds=round_of_conversation,
             claim=claim,
             finish_reason=finish_reason,

             )


def main(arg):
    data = pd.read_csv(arg.data_path)

    r''' iterate through dataset and starts conversations'''

    for i in tqdm([int(arg.claim_number)]):

        r''' Initialize the Moderator Agent'''

        moderator_agent_1 = ModeratorAgent(model=ModelType.PaLM_TEXT_GENERATION,
                                           prompt_instruction_path_moderator_terminator='prompts/moderator/%s.txt' % arg.moderator_terminator_instruction_palm,
                                           prompt_instruction_path_moderator_tag_checker='prompts/moderator/%s.txt' % arg.moderator_tag_checker_instruction_palm,
                                           prompt_instruction_path_moderator_topic_checker='prompts/moderator/%s.txt' % arg.moderator_topic_checker_instruction_palm,
                                           variables=get_variables(data.loc[i], AgentType.DEBATER_AGENT)
                                           )
        moderator_agent_2 = ModeratorAgent(model=ModelType.PaLM_TEXT_GENERATION,
                                           prompt_instruction_path_moderator_terminator='prompts/moderator/%s.txt' % arg.moderator_terminator_instruction_palm,
                                           prompt_instruction_path_moderator_tag_checker='prompts/moderator/%s.txt' % arg.moderator_tag_checker_instruction_palm,
                                           prompt_instruction_path_moderator_topic_checker='prompts/moderator/%s.txt' % arg.moderator_topic_checker_instruction_palm,
                                           variables=get_variables(data.loc[i], AgentType.DEBATER_AGENT))

        moderator_agent_3 = ModeratorAgent(model=ModelType.PaLM_TEXT_GENERATION,
                                           prompt_instruction_path_moderator_terminator='prompts/moderator/%s.txt' % arg.moderator_terminator_instruction_palm,
                                           prompt_instruction_path_moderator_tag_checker='prompts/moderator/%s.txt' % arg.moderator_tag_checker_instruction_palm,
                                           prompt_instruction_path_moderator_topic_checker='prompts/moderator/%s.txt' % arg.moderator_topic_checker_instruction_palm,
                                           variables=get_variables(data.loc[i], AgentType.DEBATER_AGENT))
        moderator_agent_4 = ModeratorAgent(model=ModelType.GPT_4_0613,
                                           prompt_instruction_path_moderator_terminator='prompts/moderator/%s.txt' % arg.moderator_terminator_instruction_gpt,
                                           prompt_instruction_path_moderator_tag_checker='prompts/moderator/%s.txt' % arg.moderator_tag_checker_instruction_gpt,
                                           prompt_instruction_path_moderator_topic_checker='prompts/moderator/%s.txt' % arg.moderator_topic_checker_instruction_gpt,
                                           variables=get_variables(data.loc[i], AgentType.DEBATER_AGENT
                                                                   ))
        moderator_agent_5 = ModeratorAgent(model=ModelType.GPT_3_5_TURBO_0613,
                                           prompt_instruction_path_moderator_terminator='prompts/moderator/%s.txt' % arg.moderator_terminator_instruction_gpt,
                                           prompt_instruction_path_moderator_tag_checker='prompts/moderator/%s.txt' % arg.moderator_tag_checker_instruction_gpt,
                                           prompt_instruction_path_moderator_topic_checker='prompts/moderator/%s.txt' % arg.moderator_topic_checker_instruction_gpt,
                                           variables=get_variables(data.loc[i], AgentType.DEBATER_AGENT
                                                                   ))

        r''' Initialize the Persuader Agent Model Config'''
        persuader_agent_model_config = ChatGPTConfig(temperature=1.0,
                                                     presence_penalty=0.0,
                                                     frequency_penalty=0.0
                                                     )

        r''' Initialize the Persuader Agent'''
        persuader_agent = PersuaderAgent(
            model=ModelType.GPT_3_5_TURBO_0613,
            model_helper=ModelType.GPT_3_5_TURBO_0613,
            model_config=persuader_agent_model_config,
            helper_prompt_instruction_path='prompts/helper/%s.txt' % arg.helper_prompt_instruction,
            prompt_instruction_path='prompts/persuader/%s.txt' % arg.persuader_instruction,
            variables=get_variables(data.loc[i], AgentType.PERSUADER_AGENT),
            memory_prompt_instruction_path='prompts/summary/%s.txt' % arg.memory_instruction,
            helper_feedback=False)

        if arg.helper_prompt_instruction != 'No_Helper':
            if not persuader_agent.helper_feedback_switch:
                print('check the setting1')
                break
        else:
            if persuader_agent.helper_feedback_switch:
                print('check the setting2')
                break

        r''' Initialize the Debater Agent Model Config'''

        debater_agent_model_config_gpt = ChatGPTConfig(temperature=1.0,
                                                       presence_penalty=0.0,
                                                       frequency_penalty=0.0
                                                       )

        r''' Initialize the Debater Agent'''
        debater_agent = DebaterAgent(
            model=ModelType.GPT_3_5_TURBO_0301,
            model_config=debater_agent_model_config_gpt,
            prompt_instruction_path='prompts/debater/%s.txt' % arg.debater_instruction,
            variables=get_variables(data.loc[i], AgentType.DEBATER_AGENT),
            memory_prompt_instruction_path='prompts/summary/%s.txt' % arg.memory_instruction,
        )
        chat_id = uuid.uuid1()
        run(persuader_agent, debater_agent, moderator_agent_1, moderator_agent_2, moderator_agent_3, moderator_agent_4,
            moderator_agent_5, arg, str(data.loc[i]['id'], ),
            str(chat_id), str(data.loc[i]['claim']), False)

        time.sleep(1)


if __name__ == '__main__':

    arg = define_arguments()
    palm.configure(api_key=arg.api_key_palm)
    openai.api_key = arg.api_key_openai
    main(arg)
