<<<<<<< HEAD
# 🧬 Evolução Real
### Simulação Evolutiva Autônoma para Android

> Controle o DNA. Molde o ambiente. Veja a vida encontrar um caminho.

---

## 🎮 O Jogo

Você não controla uma criatura — você controla a **evolução em si**.

- Configure um planeta: temperatura, água, radiação, vulcões, recursos
- Crie o DNA inicial da primeira espécie
- O tempo passa automaticamente — espécies evoluem, se adaptam, morrem
- Use **Pontos de Influência** para intervir (modo Deus) ou apenas observe (modo Cientista)
- Feche o app e volte depois: o mundo continuou sem você

### Fases da Evolução
`Microscópica → Aquática → Terrestre → Predatória → Inteligente → Civilização → Tecnológica`

### Mecânicas
- 🧬 **DNA com 9 genes** que mutam a cada geração
- 🌍 **Ambiente dinâmico** que muda com o tempo
- ⚔️ **Predação** entre espécies próximas
- 🌋 **Catástrofes** e eventos vulcânicos aleatórios
- 🌱 **Especiação** — uma espécie se divide em duas
- ⏰ **Simulação offline** — o mundo evolui enquanto você está fora

### Modos
| Modo | Descrição |
|------|-----------|
| 🔬 Cientista | Apenas observe. Sem interferência. |
| ⚡ Deus | Use pontos de influência para moldar o destino. |
| 💀 Hardcore | Uma tentativa. Se extinguir, acabou. |

---

## 🚀 Como Gerar o APK via GitHub

### 1. Criar repositório no GitHub
```bash
git init
git add .
git commit -m "🧬 Evolução Real - inicial"
git remote add origin https://github.com/SEU_USUARIO/evolucao-real.git
git push -u origin main
```

### 2. GitHub Actions compila automaticamente
Ao fazer `push` na branch `main`, o workflow roda e:
- Compila o APK com Buildozer
- Cria um **Release** com o APK para download
- Disponível em: `Repositório → Releases → Assets`

### 3. Instalar no Android
1. Baixe o `.apk` nos Releases
2. Android: **Configurações → Segurança → Fontes desconhecidas** ✅
3. Abra o `.apk` e instale

---

## 🛠️ Estrutura do Projeto

```
evolucao_real/
├── main.py                    # Jogo completo (arquivo único)
├── buildozer.spec             # Config de compilação Android
├── .github/
│   └── workflows/
│       └── build-apk.yml     # GitHub Actions → APK automático
└── README.md
```

---

## ⚙️ Executar localmente (PC)

```bash
pip install kivy==2.3.0
python main.py
```

---

## 📦 Compilar APK localmente (Linux/Mac)

```bash
pip install buildozer cython==0.29.37
buildozer android debug
# APK gerado em: bin/evolucaoreal-1.0.0-arm64-v8a-debug.apk
```

---

## 🧬 Tecnologias

- **Python 3.11** — Lógica do jogo e engine evolutiva
- **Kivy 2.3.0** — Interface gráfica cross-platform
- **Buildozer** — Empacotamento para Android
- **GitHub Actions** — CI/CD para gerar APK automaticamente
=======
# Apkjogo
>>>>>>> f412f314a8b5c1371914de0ec67069175fb19f79
