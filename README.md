# AaC-Req-QA

An AaC plugin to perform automated quality checks for the shall statements in your AaC model.

This plugin will scan your architecture for any `req` entries and will use an LLM to evaluate
the quality of the `shall` field.  The plugin is configured to evaluate your shall statement
using the following attributes:

- Unambiguous: The requirement should be simple, direct, and precise with no room for interpretation.
- Testable (verifiable): The requirement should be testable, and it should be possible to verify that the system meets the requirement.  Preferable the requirement should be verifiable by automated acceptance test, automated analysis, or demonstration rather than inspection.  If inspection is the only rational means of verification it will have a lower rating.
- Clear: The requiremet should be concise, terse, simple, and precise.
- Correct:  The requirement should not have any false or invalid assertions.
- Understandable:  The requirement should be easily understood by all stakeholders.
- Feasible: The requirement should be realistic and achievable.
- Independent:  The requirement should stand-alone and not be dependent on other requirements.
- Atomic: The requirement should be a single, discrete, and indivisible statement.
- Necessary: The requirement should be necessary to the system and not be redundant or superfluous.
- Implementation-free: The requirement should not specify how the system will be implemented.  It should only specify what the system should do, not how it should do it.

If the `shall` is evaluated to be of sufficient quality, the `aac check` will pass.  Otherwise, you will receive a
failure message produced by the AI with an assessment of each attribute and an overall score.  Failure results
from an overall score of `C (Medium)` or lower from the AI.

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

- AAC_AI_URL:  The usl of the LLM endpoint.  Example:  https://localhost:11434/v1 
- AAC_AI_MODEL:  The name of the LLM model.  Example:  mistral
- AAC_AI_KEY:  The access key for the API.  If using a local model, any value will work but it must not be empty or missing.  Example: not-a-real-key

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