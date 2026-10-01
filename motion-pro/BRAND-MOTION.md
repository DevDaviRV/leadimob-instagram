# Leadimob — BRAND-MOTION (tokens e regras para vídeo)

## Posicionamento
- Corretor digital (agente de IA) no WhatsApp Business do corretor/imobiliária, treinado no catálogo. Não é chatbot genérico.
- Mensagem central: "Você já paga para gerar lead. A Leadimob ajuda a não perder esse lead no WhatsApp."
- ICP: imobiliárias pequenas / times 3–20 corretores; secundário corretor autônomo.
- IA apoia o corretor, nunca substitui. "A IA cuida do operacional. Você cuida do relacionamento."
- CTA padrão: Solicitar demonstração (nunca "teste grátis").

## Funcionalidades que podem aparecer (implementadas no site em set/2026)
Resposta 24h no WhatsApp (API oficial Meta) · consulta ao catálogo real · envio de fotos · qualificação (intenção, região, orçamento, urgência, temperatura quente/morno/frio) · agendamento de visita conforme regras · Kanban/funil que se atualiza com resumo · follow-up e reengajamento · Site Catálogo com captação no WhatsApp (Pro+) · simulador de financiamento (quando habilitado) · transcrição de áudio e leitura de imagem · chama o corretor em negociação.
NÃO mostrar como pronto: DM Instagram, geração de posts (em desenvolvimento).

## Proibições
Sem números sem fonte (3x vendas, 500+ corretores, 98%, tempo de resposta em segundos cravado, conversão). Sem "primeira plataforma", "100% seguro", "venda garantida". Sem preços salvo confirmação (conflito 147/247/547 x 247/547).
LID = só mascote, detalhe visual discreto (fecho). Nunca protagonista, nunca "a IA", nunca executa ações.

## Voz
- Narração: ElevenLabs, Bianca - Smooth and Sophisticated (pt-BR), voice_id 9LwXyqQB0mUwtLRsS227. Davi gera e envia o mp3; Claude sincroniza.
- Grafia fonética: "Lídimob", "I.A.", "C.R.M.". CPS estimado 14,5.

## Cor (sistema de ads, fundo dark)
- Base #0A0E14; superfícies #0F1520 / #141B28; linhas rgba(255,255,255,.08–.16); texto #FFFFFF / #C9D2E0 / #7C8799.
- Destaque/CTA #2563EB; glow/linhas #22D3EE e #7DD3FC; sucesso #34D399; alerta âmbar #F59E0B (só "sem resposta/esfriando").
- Institucional claro: petróleo #0B5C73, #084255, #ECF6F9.
- Proporção: ~70% base escura, ~20% neutros/branco, ≤10% azul/ciano; verde e âmbar pontuais.
- Evitar roxo, gradiente genérico de IA, vermelho fora de alerta, humanos gerados.

## Tipografia
Inter (@fontsource/inter) 400/500/600/700/800. Títulos 800 com tracking negativo. Labels em caixa alta 600 com tracking .14em.
Logo: sempre o PNG oficial (hero-export/motion/img/leadimob-logo.png), sobre cartão claro (o "eadi" é escuro). Nunca redigitar.

## Elementos proprietários
1. Jornada do lead: linha de luz ciano ligando WhatsApp → qualificação → imóvel → visita → funil.
2. Símbolo do logo (barra + dois triângulos, construção em public/logohtml.html): wipes, máscaras, transições.
3. UI de produto: bolhas WhatsApp, pills de notificação, cards de imóvel, Kanban.

## Área segura 9:16
Texto essencial entre y≈200 e y≈1520 de 1920; margens ≥72px; fora da faixa direita de botões do Reels.
