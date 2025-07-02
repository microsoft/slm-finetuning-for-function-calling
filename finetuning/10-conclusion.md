# Congratulations!

You made it to the end!

Here are the things that we have learned:

- What are small language models, and different ways to run them.
- What is function calling?
- What is finetuning? Why and when we want to use it?
- How to structure your dataset so it is ready for finetuning.
- The importance of chat templates and tokenizers, and how you can use them to transform your data to
  the format that the model expects.
- How to finetune a small language model using the `transformers` library, and how to tell if it's working
- How to test your finetuned model.

## Challenges You Might Have Encountered

While the finetuning an SLM can be a useful technique, you may have already experienced some of the challenges that come with it. When running the labs you might have found that the finetuning steps took a long time to complete, or even timed out and failed due to the limitations of the GPU, CPU, or disk resources on the machine you ran these labs on.

If you are planning to use this technique in a production environment, you will want to consider how you can scale up your resources. You should also weigh up finetuning against other techniques.

# What's next?

But the journey is not over yet!

## Function calling in the real world

As you might have noticed (and eventually will, in the evaluation lab), that our model performs really well, almost all the time! But we were working with just a toy dataset, and in reality, the use cases and the functions we need to work with can be much more complex. In such scenarios, we'll need to iteratively work on the data, testing out different configurations for finetuning, and even ask the question whether finetuning is even the right approach!

If that sounds too real, then yes, it is real 😆. In fact, there were multiple projects at Microsoft where we needed to finetune small language models for controlling car's functionalities. The following report tells us about an engagement we worked with TomTom. It summarises our challenges (hint: data was a major part), the hypotheses, the experiments, what worked, and what didn't.

[TomTom - SLM-based in car assistant](https://microsofteur-my.sharepoint.com/:b:/g/personal/vuquy_microsoft_com/EdGwquXsLVFNlp5Q9NYtO3kB1zOYl2mOOCBHKqXWWLWaig?e=Qo0sLp)

We hope you enjoy reading this as much as we enjoyed writing it, and if you have further questions, please contact Quy Vu (vuquy@microsoft.com)!

## Optimise the model even further

There are still other things we can do to make the model even smaller and faster. In some cases, these are a must if you want to run the model on a mobile device or an edge device. Here are some pointers:

### Quantisation techniques

Quantisation techniques involve reducing the precision of the model, such as converting 32-bit floating-point numbers to lower-bit integers (e.g., 8-bit or 4-bit). This significantly reduces model size, memory usage, and computational requirements, enabling faster inference and deployment on resource-constrained devices like smartphones or edge hardware. Despite lowering numerical precision, sophisticated quantization methods preserve most of the model's accuracy.

Here are the 2 favourite techniques:

- **Activation-aware Weight Quantization (AWQ):** This focuses on preserving the most important parameters in the model that are crucial for model performance. AWQ identifies a small fraction of weights (0.1-1%) that significantly affect quantization error by utilizing activation magnitude. ([Paper](https://arxiv.org/abs/2306.00978))

- **Generative Pre-trained Transformer Quantization (GPTQ):** Similar to AWQ, this employs several optimisation techniques, including arbitrary order insight and lazy batch updates, to simplify the quantization process while maintaining model accuracy. ([Paper](https://arxiv.org/abs/2210.17323))

### ONNX Runtime optimisation

ONNX Runtime (ORT) is designed to optimise and package models ONNX (Open neural network exchange) format, which makes the model platform agnostic. It supports models from various frameworks like PyTorch, TensorFlow, and scikit-learn, and is compatible with diverse hardware. It speeds up inferency through optimisation techniques such as graph pruning, kernel fusion, hardware-specific acceleration, etc. Usually, model's performance is not impacted as the actual logic are not changed, just how the operations were executed.

- ONNX runtime: https://onnxruntime.ai/
- ONNX runtime for GenAI: https://github.com/microsoft/onnxruntime-genai

### Constrained generation with Guidance

Constrained generation basically uses a set of rules (which we can define) to help the model narrow down on what token it should generate next. In theory, this should help with accuracy. **HOWEVER**, experiments have shown that this was not always the case (We're still puzzled by this). If you are curious, please reach out to Quy Vu!

One way to do this is through the `guidance` library: https://github.com/guidance-ai/guidance
