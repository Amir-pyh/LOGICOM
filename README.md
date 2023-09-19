# LOGICOM (To be updated)

[How susceptible are LLMs to Logical Fallacies?](https://arxiv.org/abs/2308.09853)

This work investigates the rational thinking capability of
Large Language Models (LLMs) in multi-round argumentative debate
we present **Log**ic **Co**mpetence **M**easurement Benchmark (LOGICOM), a diagnostic benchmark to assess the robustness of LLMs against logical fallacies.

<figure>
  <img src="https://github.com/Amir-pyh/LOGICOM/blob/main/figs/LOGICOM.png" alt="Alt text for image" style="width:100%">
  <figcaption> LOGICOM: A demonstration of three scenarios evaluating LLMs’ reasoning skills and vulnerability to logical fallacies. </figcaption>
</figure>

## Run
```bash
python main.py --api_key_openai <insert your OpenAI API key> --api_key_palm <insert your PaLM API key> --helper_prompt_instruction <No_Helper|Fallacy_Helper|Vanilla_Helper>
```
## Results
**RQ1**: Can large language models (with fixed weights)
change their opinions through reasoning when faced with
new arguments?

We calculate the ratio of debates where the debater agent begins by disagreeing but ends up agreeing with
the persuader agent to all debates in which the debater starts
with disagreement.
<figure>
  <img src="https://github.com/Amir-pyh/LOGICOM/blob/main/figs/Q1.png" alt="Alt text for image" style="width:80%">
  <figcaption> Percentage of instances in which the debater agent changes
its stance from disagreement to agreement. </figcaption>
</figure>

**RQ2**:Are large language models susceptible to fallacious
reasoning?
To address this question, we use the two analysis approaches
described below:

In the first analysis, we aggregate the total number of successes of the persuader in each scenario and then average them over three repetitions. Then, we compare the average
number of each scenario to measure the debater agent’s susceptibility to fallacious arguments.

<figure>
  <img src="https://github.com/Amir-pyh/LOGICOM/blob/main/figs/Q2-1.png" alt="Alt text for image" style="width:100%">
  <figcaption> The average, taken from three repetitions, in which the persuader agent successfully convinced the debater agent for each scenario. </figcaption>
</figure>


In the second analysis, we calculate the total number of successes of the persuader agent for each claim in
each scenario and then average these over three repetitions
for that specific claim. This approach involves counting the
number of times the debater agent agrees with the claim out
of the three repetitions. In other words, across three repetitions, we calculate the average number of times the persuader agent successfully convinced the debater agent for
each claim in every scenario


<table>
  <tr>
    <td>
      <img src="https://github.com/Amir-pyh/LOGICOM/blob/main/figs/Q2-2-GPT-3_5.png" alt="Alt text for image 1" style="width:100%">
    </td>
    <td>
      <img src="https://github.com/Amir-pyh/LOGICOM/blob/main/figs/Q2-2-GPT-4.png" alt="Alt text for image 2" style="width:100%">
    </td>
  </tr>
</table>
<figcaption> Analyzing the susceptibility of GPT models to fallacious arguments. In the consistent agreement instances (“Three Success”), it
shows a higher level of success rate for fallacious persuader compared to the logical persuaders for both GPT-3.5 and GPT-4 debater agents.
Furthermore, the number of instances in the bar chart groups for “One Success” and “Two Success” can be seen as indications of level of
inconsistency in debater agent’s reasoning which is higher in GPT-3.5 compared to GPT-4. </figcaption>



## Citation
```bibtex
@misc{payandeh2023susceptible,
      title={How susceptible are LLMs to Logical Fallacies?},
      author={Amirreza Payandeh and Dan Pluth and Jordan Hosier and Xuesu Xiao and Vijay K. Gurbani},
      year={2023},
      eprint={2308.09853},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
