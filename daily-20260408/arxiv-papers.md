# arXiv Papers Summary — 2026-04-08

## Core Topics: Prompt Engineering, AI Agents, Context Engineering, Data Science

---

### 1. RACE: Fine-Grained LLM-Generated Text Detection (ACL 2026)
- **arXiv:** [2604.04932](https://arxiv.org/abs/2604.04932)
- **Authors:** Yang Li et al.
- **Topic:** Prompt Engineering / AI Safety
- **Summary:** 제안 RACE는 생성자(Editor)와 편집자(Creator)의 이중 역할을 모델링하여 LLM 생성 텍스트의 미세 분류(Four-class)를 수행. Rhetorical Structure Theory 기반 논리 그래프와 EDU-level feature 추출을 활용하여 LLM-polished text와 humanized LLM text를 구별. 12개 베이스라인 대비 우수 성능.

---

### 2. CoDE-Stop: Early Stopping for Large Reasoning Models via Confidence Dynamics
- **arXiv:** [2604.04930](https://arxiv.org/abs/2604.04930)
- **Authors:** Parsa Hosseni et al.
- **Topic:** Reasoning Models / Efficiency
- **Summary:** Chain-of-thought 생성 중 추론 모델의 confidence dynamics를 분석하여 early stopping 시점 결정. 올바른 추론 경로는 높은 confidence에 빠르게 도달하고, 잘못된 경로는 길고 비생산적인 추론. CoDE-Stop은 추가 학습 없이 토큰 사용량 25-50% 감소.

---

### 3. AsymGRPO: Rethinking Exploration in RLVR via Bidirectional Entropy Modulation
- **arXiv:** [2604.04894](https://arxiv.org/abs/2604.04894)
- **Authors:** Hengrui Gu et al.
- **Topic:** Reinforcement Learning / LLM Training
- **Summary:** RLVR에서 정책 엔트로피를 Informative Entropy(다양한 솔루션 경로 보존)와 Spurious Entropy(추론 패턴 침식)로 분해. AsymGRPO는 positive/negative rollout의 엔트로피를 독립적으로 제어하여 기존 엔트로피 정규화 방법보다 우수한 성능 달성.

---

### 4. SandMLE: Synthetic Sandbox for Training Machine Learning Engineering Agents
- **arXiv:** [2604.04872](https://arxiv.org/abs/2604.04872)
- **Authors:** Yuhang Zhou et al.
- **Topic:** AI Agent / ML Engineering
- **Summary:** 다중 에이전트 프레임워크가 소규모 시드 태스크에서 다양하고 검증 가능한 합성 MLE 환경 생성. 마이크로 규모 데이터셋(50-200 샘플)으로 실행 시간 13배 감소, MLE-bench-lite에서 Qwen3 시리즈 대비 20.3%-66.9%의 메달률 향상.

---

### 5. PCSA: Persona-based Client Simulation Attack for LLM Safety in Psychological Counseling
- **arXiv:** [2604.04842](https://arxiv.org/abs/2604.04842)
- **Authors:** Qingyang Xu et al.
- **Topic:** AI Safety / Red Teaming
- **Summary:** 심리 상담 도메인에서 페르소나 기반 클라이언트 시뮬레이션 공격 프레임워크. 7개 LLM(일반 + 정신건강 특화) 대상 실험에서 기존 4개 베이스라인 대비 유의미한 우위. 현재 LLM이 승인되지 않은 의학적 조언, 망상 강화, 위험 행동 조장에 취약함을 입증.

---

### 6. MERIT: Multilingual Expert-Reward Informed Tuning for Low-Resource MT
- **arXiv:** [2604.04839](https://arxiv.org/abs/2604.04839)
- **Authors:** Zhixiang Lu et al.
- **Topic:** Data Science / NLP
- **Summary:** 중국어-동남아 저자원 언어(라오스어, 미얀마어, 타갈로그어 등 5개) 번역을 위한 통합 프레임워크. Language-specific Token Prefixing + SFT + GRPO with Semantic Alignment Reward 활용. 단순 모델 스케일링보다 타겟 데이터 큐레이션과 보상 기반 최적화가 효과적.

---

### 7. LLMs vs Human Experts in Mathematical Contest in Modeling
- **arXiv:** [2604.04791](https://arxiv.org/abs/2604.04791)
- **Authors:** Yuhang Liu et al.
- **Topic:** Data Science / Mathematical Reasoning
- **Summary:** 중국 대학원 수학 모델링 콘테스트 기반 단계별 평가 프레임워크 제안. SOTA LLM은 문제 식별/정식화에서는 양호하나, 모델 풀이, 코드 구현, 결과 분석 등 실행 단계에서 지속적 결함. 이러한 갭은 모델 스케일 확대로도 해결되지 않음.

---

### 8. Hallucination Basins: A Dynamic Framework for Understanding LLM Hallucinations
- **arXiv:** [2604.04743](https://arxiv.org/abs/2604.04743)
- **Authors:** Lav Varshney et al.
- **Topic:** AI Safety / Hallucination
- **Summary:** 기하학적 동역학 시스템 프레임워크로 환각을 잠재 공간의 task-dependent basin 구조로 모델링. 사실적 질문에서는 명확한 basin 분리가 관찰되나, 요약 및 오개념이 많은 설정에서는 불안정. Geometry-aware steering으로 재학습 없이 환각 확률 감소 가능.

---

### 9. From Multi-Agent to Single-Agent: When Is Skill Distillation Beneficial?
- **arXiv:** [2604.01608](https://arxiv.org/abs/2604.01608)
- **Authors:** Binyan Xu et al.
- **Topic:** AI Agent / Multi-Agent Systems
- **Summary:** 다중 에이전트 시스템을 단일 에이전트로 증류할 때 Metric Freedom(F)이라는 사전 예측 지표 제안. F는 출력 다양성과 점수 분산 간의 결합을 Mantel test로 측정. 적응형 증류 프레임워크가 원본 MAS 성능 유지하면서 비용 8배, 지연시간 15배 감소.

---

### 10. Omni-SimpleMem: Autoresearch-Guided Discovery of Lifelong Multimodal Agent Memory
- **arXiv:** [2604.01007](https://arxiv.org/abs/2604.01007)
- **Authors:** Jiaqi Liu, Huaxiu Yao et al.
- **Topic:** AI Agent / Memory Systems
- **Summary:** 자율 연구 파이프라인이 ~50회 실험을 통해 다중 모달 메모리 프레임워크 발견. LoCoMo에서 F1 +411%(0.117→0.598), Mem-Gallery에서 +214%(0.254→0.797) 향상. 하이퍼파라미터 튜닝보다 버그 수정, 아키텍처 변경, 프롬프트 엔지니어링이 더 큰 기여.

---

## Extended Topics (Trending)

### 11. Ontology-Constrained Neural Reasoning for Enterprise Agentic Systems (FAOS)
- **arXiv:** [2604.00555](https://arxiv.org/abs/2604.00555)
- **Topic:** Enterprise AI / Neurosymbolic Architecture
- **Summary:** 3층 온톨로지(Role, Domain, Interaction) 기반 신경기호 결합 아키텍처. 5개 산업 600회 실험에서 정확도, 규제 준수, 역할 일관성 모두 유의미한 향상. LLM 파라미터 지식이 약한 도메인(베트남 현지화 등)에서 온톨로지 정합성 가치가 가장 큼.

### 12. The Persistent Vulnerability of Aligned AI Systems (PhD Thesis, UCL)
- **arXiv:** [2604.00324](https://arxiv.org/abs/2604.00324)
- **Author:** Aengus Lynch
- **Topic:** AI Safety / Alignment
- **Summary:** 4가지 AI 안전 문제(위험한 내부 연산 이해, 내장된 위험 행동 제거, 배포 전 취약성 테스트, 모델 배포자에 대한 적대 행동 예측). LAT가 sleeper agent 문제를 기존 방어 대비 700배 적은 GPU 시간으로 해결. Best-of-N jailbreak로 GPT-4o 89%, Claude 3.5 Sonnet 78% 공격 성공률.

### 13. TurboQuant: KV Cache Compression (ICLR 2026, Google)
- **Topic:** Inference Efficiency / Quantization
- **Summary:** Google Research의 TurboQuant는 KV cache를 3-bit로 양자화하면서 정확도 손실 없이 메모리 6배 이상 감소. H100에서 attention logit 연산 최대 8배 속도 향상. Random rotation + 1-bit residual 기법으로 정보 밀도 재할당.
