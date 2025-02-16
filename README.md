# Prompt Engineering for Secure Code

This repository accompanies our study **[Benchmarking Prompt Engineering Techniques for Secure Code Generation with GPT Models](https://doi.org/10.48550/arXiv.2502.06039)**. The study investigates how various prompt engineering techniques influence the security of code generation.

## Repository Structure

- **`benchmark/`**: Contains the benchmarking tool and experimental results. The benchmark systematically evaluates prompt variations and their impact on secure code generation using static analysis.
- **`agent/`**: A prototype implementation of a prompt agent that applies our findings to improve code security in LLM code generation. It extends an existing ChatGPT web interface with a security-focused prompt prefix and optional post-processing.

## Paper and Academic Usage

For full details, methodology, and results, refer to our paper  
**[Benchmarking Prompt Engineering Techniques for Secure Code Generation with GPT Models](https://doi.org/10.48550/arXiv.2502.06039)**

### Citation

If you use this repository in your research or projects, we would appreciate it if you cite our work.

M. Bruni, F. Gabrielli, M. Ghafari, and M. Kropp,
“Benchmarking prompt engineering techniques for secure code generation with gpt models,” in Proceedings of
the 2025 IEEE/ACM Second International Conference on
AI Foundation Models and Software Engineering, 2025.

**BibTeX:**
``` bibtex
@inproceedings{Bruni2025,
      title={Benchmarking Prompt Engineering Techniques for Secure Code Generation with GPT Models},
      author={Bruni, Marc and Gabrielli, Fabio and Ghafari, Mohammad and Kropp, Martin},
      year={2025},
      booktitle = {Proceedings of the 2025 IEEE/ACM Second International Conference on AI Foundation Models and Software Engineering}
}
```
