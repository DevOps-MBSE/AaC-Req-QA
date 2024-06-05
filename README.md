# AaC-Req-QA

An experimental AaC plugin to evaluate the requirement quality using GenAI Natural Language Processing.

## Usage

If you haven't already, install Architecture-as-Code (AaC):
```bash
pip install aac
```
Next install this AaC-Req-QA plugin:
```bash
pip install aac-req-qa
```

Set the environment variables needed to access an OpenAI endpoint.  This may be a commercial
endpoint in OpenAI or Azure OpenAI or a self-hosted endpoint using a tool like Ollama or vLLM.

- OPEN_AI_URL:  The usl of the LLM endpoint.  Example:  https://localhost:11434/v1 
- OPEN_AI_MODEL:  The name of the LLM model.  Example:  Mistral
- OPEN_AI_KEY:  The access key for the API.  If using a local model, any value will work but it must not be empty or missing.  Example: not-a-real-key

Now when you run `aac check my_arch_model.aac` any `req` elements defined in your model will 
have the shall statement evaluated for quality.  If the LLM determines the requirement meets
the quality guidance the constraint will pass.  Otherwise the constraint will fail.

## Caveat

Because this is using an LLM, it is a non-deterministic process and cannot be guaranteed
to perform consistently.  The LLM is tuned to reduce variation and provide reliable, repeatable
performance to the greatest extent possible, but no guarantees can be made with the current
state-of-the art LLM models.

## Attribution

We're adapting the [analize claims](https://github.com/danielmiessler/fabric/blob/main/patterns/analyze_claims/system.md) pattern
from the open source [Fabric project](https://github.com/danielmiessler/fabric) to evaluate requirements.  Huge thanks to the
Fabric team for the innovation and examples.