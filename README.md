# AaC-Req-QA

An AaC plugin to perform automated quality checks for the shall statements in your AaC model.

This plugin will scan your architecture for any `req` entries and will use an LLM to evaluate
the quality of the `shall` field.  The plugin is configured to evaluate your shall statement
using the following attributes:

- Unambiguous: The requirement should be simple, direct, and precise with no room for interpretation.
- Testable (verifiable): The requirement should be testable, and it should be possible to verify that the system meets the requirement.  Preferable the requirement should be verifiable by automated acceptance test, automated analysis, or demonstration rather than inspection.  If inspection is the only rational means of verification it will have a lower rating.
- Clear: The requirement should be concise, terse, simple, and precise.
- Correct:  The requirement should not have any false or invalid assertions.
- Understandable:  The requirement should be easily understood by all stakeholders.
- Feasible: The requirement should be realistic and achievable.
- Independent:  The requirement should stand-alone and not be dependent on other requirements.
- Atomic: The requirement should be a single, discrete, and indivisible statement.
- Necessary: The requirement should be necessary to the solution and not be redundant or superfluous.
- Implementation-free: The requirement should not specify how the solution will be implemented.  It should only specify what the solution should do, not how it should do it.

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
- AAC_AI_MODEL:  The name of the LLM model.  Example:  `mistral` for local (i.e. Ollama), `gpt-4` for OpenAI or Azure
- AAC_AI_KEY:  The access key for the API.  If using a local model, any value will work but it must not be empty or missing.  Example: not-a-real-key

If you wish to use an Azure OpenAI set the following environment variables.

- AAC_AI_TYPE:  Set to "Azure", otherwise standard OpenAI client will be used.
- AAC_AI_API_VERSION:  Set to your desired / supported API Version.  Example: 2023-12-01-preview

If you have a proxy, set the proxy environment variables.

- AAC_HTTP_PROXY:  The HTTP proxy.  Example:  http://userid:password@myproxy.myorg.com:80
- AAC_HTTPS_PROXY:  The HTTPS proxy.  Example:  https://userid:password@myproxy.myorg.com:443
- AAC_SSL_VERIFY:  Allows you to disable SSL verification.  Value must be `true` or `false` (default: `true`).

Although this is a bit cumbersome, it is necessary as there is no other way to provide configuration data
within AaC, particularly for constraint plugins.  Remember to protect your secrets when configuring these
environment variables.

### Eval-Req Command

This plugin provides a new command called `eval-req` that will execute the requirements QA
on a specified AaC file.  This will before the exact same evaluation as the constraint
run by the `check` command, but will give you all the AI output for each requirement.  This
allows you to get immediate feedback on all your requirements without all the other 
constraints being invoked.

### AaC Check

This plugin adds a constraint plugin to AaC.  Now when you run `aac check my_arch_model.aac` 
any `req` elements defined in your model will 
have the shall statement evaluated for quality.  If the LLM determines the requirement meets
the quality guidance the constraint will pass.  Otherwise the constraint will fail.

## Caveat

Because this is using an LLM, it is a non-deterministic process and cannot be guaranteed
to perform consistently.  The LLM is tuned to reduce variation and provide reliable, repeatable
performance to the greatest extent possible, but no guarantees can be made with the current
state-of-the art LLM models.

Performance is completely dependent on the performance of the LLM provided by the endpoint.
This has been tested with Azure OpenAI using GPT-4 as well as Mistral 7B run within Ollama
and had acceptable performance in both.  Performance with other models may be better or worse.

## Attribution

We're adapting the [analyze claims](https://github.com/danielmiessler/fabric/blob/main/patterns/analyze_claims/system.md) pattern
from the open source [Fabric project](https://github.com/danielmiessler/fabric) to evaluate requirements.  Huge thanks to the
Fabric team for the innovation and examples.