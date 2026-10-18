"""Gera um guião em PDF por pessoa (docs/guioes/Guiao_<Nome>.pdf).

Uso: python docs/guioes/gerar_guioes.py   (precisa de: pip install reportlab)
Para mudar um guião, edita o texto aqui e volta a correr.
Notação no texto: **negrito** e `código`.
"""
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

OUT = Path(__file__).resolve().parent
F = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Ar", F + "arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB", F + "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ArI", F + "ariali.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + "consola.ttf"))
registerFontFamily("Ar", normal="Ar", bold="ArB", italic="ArI", boldItalic="ArB")

BLUE = colors.HexColor("#1F4E79")
N = ParagraphStyle("n", fontName="Ar", fontSize=10, leading=13.5, spaceAfter=3)
SMALL = ParagraphStyle("sm", parent=N, fontSize=8.8, leading=11.5, spaceAfter=0)
T = ParagraphStyle("t", parent=N, fontName="ArB", fontSize=22, leading=27, textColor=BLUE)
SUB = ParagraphStyle("s", parent=N, fontSize=11, textColor=colors.HexColor("#555555"), spaceAfter=12)
H1 = ParagraphStyle("h1", parent=N, fontName="ArB", fontSize=14.5, leading=18, spaceBefore=12, spaceAfter=5, textColor=BLUE)
H2 = ParagraphStyle("h2", parent=N, fontName="ArB", fontSize=11, leading=14, spaceBefore=8, spaceAfter=3)
CODE = ParagraphStyle("c", fontName="Mono", fontSize=8, leading=10)
TIP = ParagraphStyle("tip", parent=N, fontSize=9.5, leading=12.5, textColor=colors.HexColor("#5A4A00"))


def fmt(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"`(.+?)`", r'<font face="Mono" size="8.8" color="#8B1A1A">\1</font>', s)


def bullets(items, numbered=False, style=N):
    li = [ListItem(Paragraph(fmt(i), style), leftIndent=14) for i in items]
    if numbered:
        return ListFlowable(li, bulletType="1", leftIndent=14, bulletFontName="ArB", bulletFontSize=9.5)
    return ListFlowable(li, bulletType="bullet", start="•", leftIndent=14, bulletFontName="Ar")


def code(txt):
    t = Table([[Preformatted(txt.strip("\n"), CODE)]], colWidths=[16 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F2F2")),
                           ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def table(rows, widths):
    data = [[Paragraph(("<b>%s</b>" % fmt(c)) if i == 0 else fmt(c), SMALL) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AAAAAA")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def tip(txt):
    t = Table([[Paragraph(fmt(txt), TIP)]], colWidths=[16 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF6D5")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def render(blocks):
    out = []
    for b in blocks:
        kind, val = b[0], b[1] if len(b) > 1 else None
        if kind == "h1": out.append(Paragraph(fmt(val), H1))
        elif kind == "h2": out.append(Paragraph(fmt(val), H2))
        elif kind == "p": out.append(Paragraph(fmt(val), N))
        elif kind == "ul": out.append(bullets(val))
        elif kind == "ol": out.append(bullets(val, numbered=True))
        elif kind == "code": out += [Spacer(1, 2), code(val), Spacer(1, 5)]
        elif kind == "tip": out += [Spacer(1, 3), tip(val), Spacer(1, 5)]
        elif kind == "table": out += [Spacer(1, 2), table(val, b[2]), Spacer(1, 6)]
        elif kind == "pb": out.append(PageBreak())
        elif kind == "plan_b": out += render(plan_b(val))
        elif kind == "keep": out.append(KeepTogether(render(val)))
    return out


# ----------------------------------------------------------------------------------------------
# Capítulo comum a todos
# ----------------------------------------------------------------------------------------------
def plan_b(pasta):
    """Para não ficar parado se o modelo base do Miguel atrasar."""
    return [
        ("h2", "Plano B: se o modelo base ainda não estiver pronto na quinta"),
        ("p", f"Não esperes. Cria um modelo de teste teu (`sandbox/{pasta}/teste.alp`) com um **Stock falso**, que tem "
              "os mesmos nomes do verdadeiro. Os teus agentes funcionam com ele, e quando o modelo base sair só copias "
              "os teus agentes para lá (Ctrl+C / Ctrl+V no Projects)."),
        ("ol", [
            "Novo modelo (time units: minutes). No Main: parâmetro `initialPrice` 0.5, variáveis `fundamentalValue` "
            "(Initial value `initialPrice`) e `nextOrderId` long 0, e uma função `broadcast(String msg)` vazia.",
            "**Single agent** `stock`, do tipo `Stock`. Variáveis `lastPrice` e `ma` (Initial value `main.initialPrice`) e `halted` false.",
            "Funções do Stock falso:",
        ]),
        ("code", """
// mid (Returns double)
return lastPrice;

// order (Just action; trader Agent, side int, price double, qty int): o preço mexe um pouco no sentido da ordem
lastPrice *= 1 + side * 0.0002 * qty / 1000.0;
traceln(time() + " ordem " + (side == 1 ? "COMPRA " : "VENDA ") + qty + " @ " + price);

// cancelAll (Just action; a Agent)
// vazio
"""),
        ("p", "Event `walk` no Stock falso (Rate 1): `lastPrice *= 1 + normal(0.002, 0); ma = 0.98 * ma + 0.02 * lastPrice;`"),
    ]


def common(pasta):
    return [
        ("h1", "0. Como trabalhar (lê isto primeiro)"),
        ("h2", "Uma vez só"),
        ("ol", [
            "Aceita o convite do GitHub que chega ao teu email (repositório **sad-euronext-g2**).",
            "Instala o **GitHub Desktop** (desktop.github.com) e entra com a tua conta.",
            "No GitHub Desktop: **File → Clone repository → sad-euronext-g2 → Clone**. Fica uma pasta no teu PC "
            "(por defeito em Documentos\\GitHub\\sad-euronext-g2).",
            "Confirma com o grupo que **todos usam a mesma versão do AnyLogic** (Help → About). Um modelo gravado "
            "numa versão mais recente pode não abrir numa mais antiga.",
        ]),
        ("h2", "Todos os dias"),
        ("ol", [
            "GitHub Desktop: **Fetch origin → Pull** (trazes o que os outros fizeram).",
            "AnyLogic: **File → Open** e abres o teu `.alp` dentro da pasta do repositório. Não reinstalas nada: "
            "o GitHub só mantém a pasta sincronizada.",
            "Trabalhas e gravas (Ctrl+S).",
            "GitHub Desktop: escreves uma mensagem curta (ex.: `João: fundamentalista com statechart`) → "
            "**Commit to main → Push origin**.",
        ]),
        ("h2", "Onde trabalhas"),
        ("ul", [
            "`model/Euronext_Main.alp` é o modelo principal e **só o Miguel o edita**.",
            f"Tu trabalhas em `sandbox/{pasta}/`. Depois do Miguel publicar o modelo base, copia "
            f"`model/Euronext_Main.alp` para a tua pasta com outro nome (ex.: `sandbox/{pasta}/{pasta}.alp`) e "
            "abre esse. Na tua cópia podes mexer em tudo, incluindo no Main.",
            "Quando a tua peça funcionar: commit + push e avisa no grupo. O Miguel abre os dois modelos no AnyLogic e, "
            "no painel **Projects**, copia o teu agente (Ctrl+C) e cola-o no modelo principal (Ctrl+V). Isto só "
            "funciona sem erros se usares os nomes do `docs/CONTRATO.md`.",
            "Se estragares a tua cópia: GitHub Desktop → separador **History** → botão direito num commit antigo → "
            "**Revert**. Ou voltas a copiar o modelo principal.",
        ]),
        ("h2", "AnyLogic em 1 minuto"),
        ("table", [
            ["Coisa", "Para que serve", "Onde está"],
            ["Agent type", "um tipo de participante (ex.: `Fundamentalist`)", "Palette → Agent → arrastar **Agent**"],
            ["Population", "muitos agentes do mesmo tipo dentro do Main", "assistente do Agent → *Population of agents*"],
            ["Parameter", "valor fixo que muda de cenário para cenário (ex.: `nChartists`)", "Palette → Agent → Parameter"],
            ["Variable", "valor que muda durante a simulação (ex.: `cash`)", "Palette → Agent → Variable"],
            ["Function", "bloco de código que se chama pelo nome", "Palette → Agent → Function"],
            ["Event", "código que corre num instante ou de X em X minutos", "Palette → Agent → Event"],
            ["Statechart", "os estados de um agente e o que o faz mudar de estado", "Palette → Statechart"],
            ["Process Modeling Library", "blocos de filas (Enter, Queue, Hold, Delay, Sink…)", "Palette → Process Modeling Library"],
            ["`main`", "dentro de qualquer agente, `main` dá acesso ao Main (ex.: `main.stock.mid()`)", "—"],
        ], [3.4, 7.6, 5.0]),
        ("h2", "Como desenhar um statechart"),
        ("ol", [
            "Abre o agente: duplo clique no tipo (ex.: `Fundamentalist`) no painel **Projects**.",
            "Palette → **Statechart** → arrasta **Statechart Entry Point**. O nome fica `statechart`; não o mudes "
            "(o Miguel chama `statechart` em todos os agentes).",
            "Arrasta um **State**, encosta-lhe a ponta do Entry Point e dá-lhe o nome em **Name**.",
            "Transição: na Palette faz **duplo clique em Transition** (fica em modo de desenho), clica na borda do "
            "estado de origem e depois na borda do estado de destino.",
            "Clica na transição e escolhe **Triggered by**: **Rate** (acontece em média X vezes por minuto, ao acaso: "
            "“de vez em quando decide”); **Timeout** (X minutos depois de entrar no estado; com Timeout 0 o agente faz "
            "a ação e volta logo); **Message** (quando chega uma mensagem: Message type `String`, Fire transition "
            "*On particular message*, Message `\"HALT\"`); **Condition** (usada à saída de um Branch).",
            "**Branch** (o losango na Palette Statechart) serve para decidir. Cada seta que sai dele tem uma Condition; "
            "uma tem de ser **Default** (a que se segue se nenhuma outra for verdadeira).",
            "Código: cada estado tem **Entry action** (corre ao entrar) e cada transição tem **Action** (corre ao passar) "
            "e **Guard** (condição extra para a transição poder acontecer).",
            "**Estado composto**: desenha um State grande e arrasta outros para dentro; dentro dele põe um **Initial "
            "State Pointer** apontado para o primeiro estado. Uma seta que sai do estado grande vale para todos os "
            "de dentro: é assim que se faz o `HALT` (de qualquer estado, o agente vai para `Halted`).",
            "Testar: carrega em Run; na barra de cima da janela da simulação escolhe o agente (ex.: "
            "`fundamentalists[0]`) e vês o estado ativo a verde. Para escrever na consola: `traceln(\"texto \" + x);`.",
        ]),
        ("tip", "Este guião tem o código para colar. Onde aparece **Entry action**, **Action** ou o nome de uma função, "
                "copia o bloco cinzento para esse campo. Se o AnyLogic não aceitar `statechart.receiveMessage(msg)`, "
                "usa `statechart.fireEvent(msg)`, que faz o mesmo."),
        ("pb",),
    ]


# ----------------------------------------------------------------------------------------------
# Miguel
# ----------------------------------------------------------------------------------------------
MIGUEL = [
    ("h1", "Resumo das tuas semanas"),
    ("table", [
        ["Semana", "Entrega concreta"],
        ["1 (17–24 out)", "GitHub (feito pelo Claude Code). Modelo base: Order, Stock com filas, matching e noise traders. **Até quinta o preço mexe num gráfico.**"],
        ["2 (24–31 out)", "Statechart do Stock com colares (±3%/±8%), reservas de 3/10 min e leilão de reabertura. Integrar o fundamentalista do João e a instrumentação da Margarida."],
        ["3 (31 out–7 nov)", "Integrar tudo (chartists, criador de mercado, notícias, dashboard). **Fase 1 a correr.**"],
        ["4 (7–14 nov)", "Velocidade do modelo e apoio à calibração."],
        ["5 (14–21 nov)", "Integrar a Fase 2 (LeveragedTrader da Margarida, Broker da Matilde) e corrigir erros."],
        ["6 (21–28 nov)", "Congelar o modelo; introdução, problema e livro de ordens no relatório."],
    ], [3.2, 12.8]),
    ("p", "A proposta diz que o livro de ordens é um **sistema de filas** feito com a Process Modeling Library. Por isso "
          "cada ordem é um agente `Order` que entra num fluxograma dentro do `Stock`: fila de espera, Hold (retém as "
          "ordens durante a reserva), filas de compra e de venda ordenadas por preço, e saída por execução ou por "
          "cancelamento (timeout = desistência)."),
    ("h1", "1. Criar o modelo (semana 1)"),
    ("ol", [
        "AnyLogic: **File → New → Model**. Model name `Euronext_Main`; Location: a pasta `model/` do repositório; "
        "**Model time units: minutes**.",
        "No `Main` cria os **parâmetros** (Palette → Agent → Parameter): `nNoise` int 30, `initialPrice` 0.5, "
        "`tickSize` 0.0001, `haltShort` 3, `haltLong` 10, `noiseRate` 1, `noiseSigma` 0.002.",
        "E as **variáveis** (Palette → Agent → Variable): `fundamentalValue` double (Initial value `initialPrice`), "
        "`nextOrderId` long 0, `dynamicThreshold` double 0.03, `staticThreshold` double 0.08, `collarsActive` boolean true.",
        "O resto do Main (cenários, ficheiros de saída e KPIs: `collarSet`, `label`, `runId`, `logEvent`…) é feito "
        "pela **Margarida** na semana 2, na cópia dela. Tu só o integras (secção 6).",
    ]),
    ("h2", "Funções do Main"),
    ("p", "**roundTick** (Returns value, double; argumento `p` double):"),
    ("code", "return Math.max(tickSize, Math.round(p / tickSize) * tickSize);"),
    ("p", "**onFill** (Just action; argumentos `t` Agent, `side` int, `q` int, `p` double). Atualiza o dinheiro e as "
          "ações de quem negociou. Descomenta uma linha por cada tipo de agente que entrar no modelo:"),
    ("code", """
if (t instanceof NoiseTrader) { NoiseTrader x = (NoiseTrader) t; x.position += side * q; x.cash -= side * q * p; }
// else if (t instanceof Fundamentalist) { Fundamentalist x = (Fundamentalist) t; x.position += side * q; x.cash -= side * q * p; }
// else if (t instanceof Chartist) { Chartist x = (Chartist) t; x.position += side * q; x.cash -= side * q * p; }
// else if (t instanceof MarketMaker) { MarketMaker x = (MarketMaker) t; x.position += side * q; x.cash -= side * q * p; }
"""),
    ("p", "**broadcast** (Just action; argumento `msg` String). Entrega a mensagem a todos; descomenta à medida que entram:"),
    ("code", """
// for (Fundamentalist a : fundamentalists) a.statechart.receiveMessage(msg);
// for (Chartist a : chartists) a.statechart.receiveMessage(msg);
// marketMaker.statechart.receiveMessage(msg);
// news.statechart.receiveMessage(msg);
traceln(time() + "  " + msg);
"""),
    ("h1", "2. Agente Order"),
    ("ol", [
        "Palette → Agent → arrasta **Agent** para o Main → **Agent type only** → Name `Order` → Animation *None* → Finish.",
        "Dentro de `Order` cria 6 variáveis: `id` long, `side` int, `price` double, `qty` int, `tSubmit` double, "
        "`trader` (Type *Other…* → `Agent`).",
    ]),
    ("h1", "3. Agente Stock: o livro de ordens como filas"),
    ("ol", [
        "Palette → Agent → arrasta **Agent** → **Single agent** → agent type `Stock`, agent name `stock` → Finish.",
        "Dentro de `Stock`, variáveis: `lastPrice`, `refPrice` e `ma` (double, Initial value `main.initialPrice`), "
        "`halted` boolean false, `volume` int 0, `lastStaticDir` int 0, `haltStart` double, `prePrice` double.",
        "Desenha este fluxograma com a Palette **Process Modeling Library** (arrasta os blocos e liga as portas):",
    ]),
    ("code", """
 enter --> holdQueue --> hold --> sideSelect --(true)--> bidBook --> bidGate --> sinkNever
                                       |                   '--(timeout)--> sinkCancelled
                                       '----(false)------> askBook --> askGate --> sinkNever
                                                           '--(timeout)--> sinkCancelled
 executed --> sinkExecuted            cancelEnter --> sinkCancelled
"""),
    ("table", [
        ["Bloco", "Tipo", "Propriedades"],
        ["enter, executed, cancelEnter", "Enter", "Agent type: `Order`"],
        ["holdQueue", "Queue", "Agent type `Order`; **Maximum capacity** marcado"],
        ["hold", "Hold", "Agent type `Order`; *Initially blocked* desmarcado"],
        ["sideSelect", "SelectOutput", "Select True output: *If condition is true*; Condition `agent.side == 1`"],
        ["bidBook", "Queue", "Maximum capacity; **Queuing: Priority-based**; Agent priority `agent.price`; **Enable exit on "
                             "timeout**, Timeout `uniform(10, 60)` minutes; **On enter** `matchEvent.restart(0);`"],
        ["askBook", "Queue", "Igual ao bidBook, mas Agent priority `-agent.price`"],
        ["bidGate, askGate", "Hold", "**Initially blocked** marcado (as ordens ficam no livro até serem executadas ou canceladas)"],
        ["sinkNever, sinkCancelled, sinkExecuted", "Sink", "—"],
    ], [4.2, 2.4, 9.4]),
    ("tip", "Põe **Agent type: Order** em todos os blocos, para o código poder usar `agent.price`. As filas por prioridade "
            "põem a melhor compra (preço mais alto) e a melhor venda (preço mais baixo) à frente e, no mesmo preço, "
            "por ordem de chegada. É exatamente o FCFS por nível de preço que está na proposta."),
    ("h2", "Funções do Stock"),
    ("p", "**order** (Just action; argumentos `trader` Agent, `side` int, `price` double, `qty` int). É esta que os investidores chamam:"),
    ("code", """
Order o = new Order();
o.id = main.nextOrderId++;
o.side = side;
o.price = main.roundTick(price);
o.qty = qty;
o.tSubmit = time();
o.trader = trader;
enter.take(o);
"""),
    ("p", "**bestBid**, **bestAsk**, **mid** e **spread** (todas Returns value, double):"),
    ("code", """
// bestBid
return bidBook.size() > 0 ? bidBook.get(0).price : Double.NaN;
// bestAsk
return askBook.size() > 0 ? askBook.get(0).price : Double.NaN;
// mid
double b = bestBid(), a = bestAsk();
if (Double.isNaN(b) || Double.isNaN(a)) return lastPrice;
return (a + b) / 2;
// spread
return bestAsk() - bestBid();
"""),
    ("p", "**cancelAll** (Just action; argumento `a` Agent):"),
    ("code", """
for (int i = bidBook.size() - 1; i >= 0; i--) {
    Order o = bidBook.get(i);
    if (o.trader == a) { bidBook.remove(o); cancelEnter.take(o); }
}
for (int i = askBook.size() - 1; i >= 0; i--) {
    Order o = askBook.get(i);
    if (o.trader == a) { askBook.remove(o); cancelEnter.take(o); }
}
"""),
    ("p", "**execute** (Just action; argumentos `b` Order, `a` Order, `p` double, `q` int):"),
    ("code", """
lastPrice = p;
volume += q;
b.qty -= q;
a.qty -= q;
main.onFill(b.trader, 1, q, p);
main.onFill(a.trader, -1, q, p);
if (b.qty == 0) { bidBook.remove(b); executed.take(b); }
if (a.qty == 0) { askBook.remove(a); executed.take(a); }
"""),
    ("p", "**collarHit** (Returns value, boolean; argumento `p` double). Na semana 1 o corpo é só `return false;`. "
          "O código verdadeiro está na secção 5."),
    ("p", "**match** (Just action):"),
    ("code", """
while (!halted && bidBook.size() > 0 && askBook.size() > 0) {
    Order b = bidBook.get(0);
    Order a = askBook.get(0);
    if (b.price < a.price) break;                            // não há cruzamento
    double p = (a.tSubmit < b.tSubmit) ? a.price : b.price;  // preço de quem já estava no livro
    if (collarHit(p)) return;                                 // abre reserva; a ordem espera pelo leilão
    execute(b, a, p, Math.min(a.qty, b.qty));
}
"""),
    ("h2", "Eventos do Stock"),
    ("ul", [
        "**matchEvent**: Trigger type *Timeout*, Mode **User control**, Action `match();`",
        "**dayEvent** (abertura de cada dia): Mode *Cyclic*, First occurrence 510, Recurrence 510, "
        "Action `refPrice = lastPrice; lastStaticDir = 0;`",
        "**maEvent** (média móvel de ~50 min para os chartists): Mode *Cyclic*, First occurrence 1, Recurrence 1, "
        "Action `ma = 0.98 * ma + 0.02 * lastPrice;`",
    ]),
    ("tip", "Se der erro ao fazer `new Order()` com o Enter: cria no Main uma população vazia `orders` (Population of "
            "agents, Initial number 0), troca a 1.ª linha de `order` por `Order o = main.add_orders();` e, nos três "
            "Sink, põe em On enter `main.remove_orders(agent);`."),
    ("h1", "4. Noise traders e gráfico (semana 1)"),
    ("ol", [
        "Palette → Agent → **Agent** → **Population of agents** → type `NoiseTrader`, population `noiseTraders`, "
        "Initial number `nNoise`.",
        "Variáveis do NoiseTrader: `cash` double 1e9, `position` int 0.",
        "Event `trade`: Trigger type **Rate**, Rate `main.noiseRate` (per minute). Action:",
    ]),
    ("code", """
int side = randomTrue(0.5) ? 1 : -1;
double p = main.stock.mid() * (1 + normal(main.noiseSigma, 0));   // AnyLogic: normal(sigma, média)
main.stock.order(this, side, p, uniform_discr(100, 1000));
"""),
    ("ol", [
        "Palette **Analysis** → **Time Plot** no Main: Value `stock.lastPrice` (título Preço) e `fundamentalValue`; "
        "Time window 510.",
        "Projects → **Simulation** → Model time: Stop **At specified time** 61200 (120 dias). **Run**.",
        "Confirma que o preço mexe. Commit `Miguel: modelo base, o preço mexe` e **avisa o grupo**: toda a gente "
        "começa a trabalhar a partir deste ficheiro.",
    ]),
    ("h1", "5. Colares, reservas e leilão (semana 2)"),
    ("p", "Regras da proposta: reserva se o preço sair de ±3% do último preço (**dinâmico**) ou de ±8% do preço de "
          "referência (**estático**; abertura ou último leilão). A reserva dura 3 min, ou 10 min se o estático voltar a "
          "disparar no mesmo sentido. Depois há um leilão de reabertura."),
    ("p", "Substitui o corpo de **collarHit**:"),
    ("code", """
if (!main.collarsActive) return false;
boolean dyn  = Math.abs(p / lastPrice - 1) > main.dynamicThreshold;
boolean stat = Math.abs(p / refPrice - 1) > main.staticThreshold;
if (!dyn && !stat) return false;
int dir = p > lastPrice ? 1 : -1;
if (stat && dir == lastStaticDir) statechart.receiveMessage("STATIC_REPEAT");
else if (stat) { lastStaticDir = dir; statechart.receiveMessage("STATIC"); }
else statechart.receiveMessage("DYNAMIC");
return true;
"""),
    ("h2", "Statechart do Stock"),
    ("code", """
             +--"DYNAMIC"------> ReservDynamic --Timeout haltShort--+
             |                                                      v
 Continuous -+--"STATIC"-------> ReservStatic  --Timeout haltShort--> Auction --Timeout 0.01--> Continuous
             |                                                      ^          (runAuction(); endHalt();)
             +--"STATIC_REPEAT"> ReservStatic10 -Timeout haltLong---+
"""),
    ("table", [
        ["Estado", "Entry action"],
        ["Continuous (inicial)", "`halted = false; matchEvent.restart(0);`"],
        ["ReservDynamic, ReservStatic, ReservStatic10", "`startHalt();`"],
        ["Auction", "`hold.unblock();` (as ordens retidas entram nos livros)"],
    ], [6, 10]),
    ("p", "As 3 transições que saem de Continuous: Triggered by **Message**, String, *On particular message* com "
          "`\"DYNAMIC\"`, `\"STATIC\"` e `\"STATIC_REPEAT\"`. Timeouts: `main.haltShort`, `main.haltShort` e "
          "`main.haltLong`. Auction → Continuous: Timeout `0.01`, Action `runAuction(); endHalt();`."),
    ("p", "**startHalt** e **endHalt** (Just action):"),
    ("code", """
// startHalt
halted = true;
hold.block();                 // ordens novas ficam na holdQueue até ao leilão
haltStart = time();
prePrice = lastPrice;
main.nHalts++;
main.broadcast("HALT");

// endHalt
main.haltsFile.println(main.label + ";" + main.runId + ";" + haltStart + ";" + time() + ";"
                       + prePrice + ";" + lastPrice);
main.timeHalted += time() - haltStart;
main.broadcast("REOPEN");
"""),
    ("tip", "As linhas com `main.nHalts`, `main.haltsFile`, `main.label`, `main.runId` e `main.timeHalted` usam a "
            "instrumentação da Margarida. Até a integrares, deixa-as comentadas com `//`."),
    ("p", "**runAuction** (Just action). Escolhe o preço que maximiza a quantidade negociada e executa tudo a esse preço único:"),
    ("code", """
double bestP = lastPrice;
int bestQ = 0;
java.util.TreeSet<Double> cands = new java.util.TreeSet<>();
for (int i = 0; i < bidBook.size(); i++) cands.add(bidBook.get(i).price);
for (int i = 0; i < askBook.size(); i++) cands.add(askBook.get(i).price);
for (double p : cands) {
    int dem = 0, sup = 0;
    for (int i = 0; i < bidBook.size(); i++) if (bidBook.get(i).price >= p) dem += bidBook.get(i).qty;
    for (int i = 0; i < askBook.size(); i++) if (askBook.get(i).price <= p) sup += askBook.get(i).qty;
    int q = Math.min(dem, sup);
    if (q > bestQ || (q == bestQ && q > 0 && Math.abs(p - lastPrice) < Math.abs(bestP - lastPrice))) {
        bestQ = q; bestP = p;
    }
}
while (bestQ > 0 && bidBook.size() > 0 && askBook.size() > 0
       && bidBook.get(0).price >= bestP && askBook.get(0).price <= bestP) {
    Order b = bidBook.get(0), a = askBook.get(0);
    execute(b, a, bestP, Math.min(a.qty, b.qty));
}
refPrice = lastPrice;         // o leilão passa a ser a nova referência estática
"""),
    ("p", "**Teste:** põe `noiseSigma = 0.01` para forçar movimentos grandes. Devem aparecer linhas na consola "
          "(`HALT`/`REOPEN`) e o preço fica parado durante 3 min. Volta a pôr 0.002."),
    ("h1", "6. Integração (semanas 2–3)"),
    ("ol", [
        "Quando alguém avisar: Pull e abre o modelo dessa pessoa e o `model/Euronext_Main.alp` (ambos ficam no Projects).",
        "No modelo da pessoa, seleciona o tipo de agente (ex.: `Fundamentalist`) → Ctrl+C → seleciona `Euronext_Main` → Ctrl+V.",
        "Arrasta o tipo, do Projects para o canvas do Main, para criar a população. Usa o nome do CONTRATO "
        "(ex.: `fundamentalists`) e em Initial number o parâmetro (`nFundamentalists`).",
        "Copia também os parâmetros novos que essa pessoa criou no Main dela (seleciona-os no canvas → Ctrl+C → Ctrl+V).",
        "Descomenta as linhas desse tipo em `onFill` e `broadcast`.",
        "**Instrumentação da Margarida** (semana 2): copia do Main dela os parâmetros e variáveis novos, os 2 Text "
        "File, o `logEvent` e o texto do *On startup* e do *On destroy*. Depois descomenta as linhas de `startHalt` "
        "e `endHalt`.",
        "Build (F7) → corrige os erros que aparecerem no painel Problems → Run → Commit `Miguel: integrado X`.",
    ]),
    ("h1", "7. Velocidade (semana 4)"),
    ("ul", [
        "Nas experiências (Parameters Variation, Optimization) não há animação, por isso correm muito mais depressa.",
        "Se a Simulation estiver lenta: Run → no fundo da janela, **Virtual time mode** (o botão da seta dupla).",
        "Se o livro ficar com milhares de ordens, reduz o timeout dos livros (ex.: `uniform(5, 30)`) e diz à Margarida (isto entra na calibração).",
    ]),
    ("h1", "8. Fase 2: integração (semana 5)"),
    ("ul", [
        "A Matilde faz o agente `Broker` inteiro (fila e statecharts) e a Margarida o `LeveragedTrader`. Tu integras os dois "
        "como na secção 6 e acrescentas as linhas deles em `onFill` e `broadcast`.",
        "Confirma que as ordens dos alavancados passam pelo broker (`main.brokers.get(0).order(...)`) e chegam ao `stock.enter`.",
        "Com o tempo que sobra, ajuda quem estiver atrasado. Tu conheces o motor melhor que ninguém.",
    ]),
    ("h1", "9. Semana 6"),
    ("ul", [
        "Último commit com a mensagem `VERSÃO FINAL`. A partir daí ninguém mexe no `model/`.",
        "No relatório: Introdução e Definição do problema (partem das secções da proposta) e a descrição do livro de ordens como sistema de filas (secção 3 deste guião).",
    ]),
]

# ----------------------------------------------------------------------------------------------
# João
# ----------------------------------------------------------------------------------------------
JOAO = [
    ("h1", "Resumo das tuas semanas"),
    ("table", [
        ["Semana", "Entrega concreta"],
        ["1 (17–24 out)", "**Dados do BCP** (Python + Claude Code): preços diários, estatísticas-alvo, arquivo intradiário. "
                          "Perceber os statecharts e desenhar os deste guião. Quando o modelo base sair: começar o Fundamentalist."],
        ["2 (24–31 out)", "**Fundamentalist a funcionar.** Tabela de metas (calmo, BES, COVID)."],
        ["3 (31 out–7 nov)", "**Chartist com rede e efeito manada.** Testar o `kpis.py` com as primeiras corridas da Margarida."],
        ["4 (7–14 nov)", "**Calibração**: `compare_model.py` + afinar os investidores com a Margarida. Validação (ESMA e BES)."],
        ["5 (14–21 nov)", "KPIs dos cenários (`kpis.py`). Fase 2: MarketMaker em stress."],
        ["6 (21–28 nov)", "`kpis.xlsx` final para a Matilde. Relatório: investidores, dados e resultados."],
    ], [3.2, 12.8]),
    ("tip", "Tens o Claude Code: usa-o para tudo o que é Python. Abre-o na pasta do repositório e pede, por exemplo, "
            "“corre o download_daily.py e o target_stats.py e explica-me os resultados”, ou “o kpis.py deu este erro: …”. "
            "Os scripts já estão em `scripts/`."),
    ("h1", "1. Semana 1: perceber antes de programar"),
    ("ol", [
        "Abre o **Market Model** das aulas e repara em 3 coisas: (a) como o statechart muda de estado com Rate e "
        "Timeout; (b) como um agente manda uma mensagem a outro (`send(...)`) e como a transição Message reage; "
        "(c) onde se define a rede de contactos (Main → Properties → **Space and network**).",
        "Lê o capítulo 0 deste guião.",
        "Desenha em papel os statecharts do Fundamentalist e do Chartist (secções 2 e 4) e vê se percebes cada seta. "
        "As dúvidas vão para `sandbox/joao/duvidas.md`. Não precisas de escrever mais nenhum documento: as regras estão aqui.",
        "Quando o Miguel publicar o modelo base: Pull → copia `model/Euronext_Main.alp` para `sandbox/joao/joao.alp` → abre esse.",
    ]),
    ("plan_b", "joao"),
    ("h1", "1b. Semana 1: dados do BCP (Python)"),
    ("ol", [
        "Instala o Python (python.org/downloads; no instalador marca **“Add python.exe to PATH”**). Depois, na pasta do "
        "repositório: `pip install -r scripts/requirements.txt` (ou pede ao Claude Code para o fazer).",
        "Preços diários desde 2010: `python scripts/download_daily.py` → `data/raw/bcp_daily.csv`.",
        "Metas do período calmo: `python scripts/target_stats.py` → `data/processed/target_stats_2023-01-01_2024-12-31.xlsx`.",
        "Períodos de stress: `python scripts/target_stats.py 2014-06-01 2014-09-30` (BES) e "
        "`python scripts/target_stats.py 2020-02-15 2020-04-30` (COVID).",
        "Dados de 1 minuto: `python scripts/archive_intraday.py`. **Corre isto 2 vezes por semana até dezembro** (ex.: "
        "segunda e quinta), porque o Yahoo só guarda ~7 dias. Põe um alarme. Cada corrida acrescenta ao mesmo ficheiro sem duplicar.",
        "Commit + push de `data/` (mensagem `João: dados BCP`).",
    ]),
    ("table", [
        ["Estatística (target_stats)", "O que quer dizer"],
        ["volatilidade_diaria", "desvio-padrão dos retornos diários: o “tamanho normal” de um dia"],
        ["curtose_excesso", "caudas pesadas: 0 seria normal; ações reais têm muito mais (dias extremos mais frequentes)"],
        ["pct_dias_var_maior_3pct", "% de dias com subida ou descida > 3%: é o que faz disparar o colar dinâmico"],
        ["autocorr_abs_retornos_lag1", "clustering de volatilidade: dias agitados vêm seguidos"],
        ["pior_dia / melhor_dia", "extremos; servem para comparar com o choque do cenário BES"],
    ], [5.5, 10.5]),
    ("h2", "Semana 2: tabela de metas"),
    ("p", "Junta num Excel `data/processed/metas.xlsx` três colunas (Calmo 2023–24, BES 2014, COVID 2020) com as linhas do "
          "`target_stats` e a queda máxima de cada período (do pico ao mínimo). Pede ao Claude Code um script que faça isto "
          "a partir do `bcp_daily.csv`. Vai para o relatório como “factos estilizados”."),
    ("h1", "2. Fundamentalist: compra barato, vende caro"),
    ("p", "Cada fundamentalista tem uma estimativa do valor da ação: o valor fundamental mais um erro pessoal. Se o "
          "preço está abaixo, compra; se está acima, vende; durante uma reserva, espera."),
    ("ol", [
        "No Main da tua cópia, parâmetros: `nFundamentalists` int 40, `fundRate` 0.2, `fundBand` 0.01.",
        "Palette → Agent → **Agent** → **Population of agents** → type `Fundamentalist`, population `fundamentalists`, "
        "Initial number `nFundamentalists`.",
        "Variáveis do Fundamentalist: `cash` double 5000, `position` int 10000, `bias` double com Initial value `normal(0.02, 0)`.",
        "Função **value** (Returns value, double): `return main.fundamentalValue * (1 + bias);`",
        "Desenha o statechart:",
    ]),
    ("code", """
 +-------------------------------- Active --------------------------------+
 |  (inicial) Watching --Rate fundRate--> <decide>                         |
 |                                           |-- barato -------> Buying     |
 |                                           |-- caro ---------> Selling    |
 |                                           |-- sem dinheiro -> OutOfCash  |
 |                                           '-- default ------> Watching   |
 |  Buying, Selling --Timeout 0--> Watching                                |
 |  OutOfCash --Timeout 60--> Watching                                     |
 +-------------------------------------------------------------------------+
      | Message "HALT"                          ^ Message "REOPEN"
      v                                         |
    Halted -------------------------------------+
"""),
    ("table", [
        ["Transição", "Triggered by", "Condition / Guard"],
        ["Watching → decide", "Rate `main.fundRate`", "—"],
        ["decide → Buying", "Condition", "`main.stock.mid() < value() * (1 - main.fundBand) && cash > main.stock.mid() * 100`"],
        ["decide → Selling", "Condition", "`main.stock.mid() > value() * (1 + main.fundBand) && position >= 100`"],
        ["decide → OutOfCash", "Condition", "`cash < main.stock.mid() * 100 && position < 100`"],
        ["decide → Watching", "Default", "—"],
        ["Buying → Watching, Selling → Watching", "Timeout 0", "—"],
        ["OutOfCash → Watching", "Timeout 60", "volta a tentar uma hora depois"],
        ["Active → Halted", "Message `\"HALT\"`", "—"],
        ["Halted → Active", "Message `\"REOPEN\"`", "entra outra vez em Watching (Initial State Pointer)"],
    ], [4.4, 3.4, 8.2]),
    ("p", "**Buying → Entry action:**"),
    ("code", """
double m = main.stock.mid();
double p = Math.min(value(), m * 1.002);                              // paga no máximo o que acha justo
int q = (int) Math.min(cash / p, 100 + 20000 * (value() / m - 1));    // compra mais quanto mais barato estiver
if (q >= 100) main.stock.order(this, 1, p, q);
"""),
    ("p", "**Selling → Entry action:**"),
    ("code", """
double m = main.stock.mid();
double p = Math.max(value(), m * 0.998);
int q = (int) Math.min(position, 100 + 20000 * (m / value() - 1));
if (q >= 100) main.stock.order(this, -1, p, q);
"""),
    ("p", "Na tua cópia, no Main, descomenta as linhas do Fundamentalist nas funções `onFill` e `broadcast` (o Miguel faz o mesmo no principal)."),
    ("p", "**Teste:** corre; o preço deve oscilar à volta do valor fundamental. Escolhe `fundamentalists[0]` na barra de "
          "cima e vê o statechart a mudar. Para ver se ele reage, muda o `initialPrice` para 0.45 com o `fundamentalValue` "
          "a 0.50: o preço deve subir. Commit `João: fundamentalista` e avisa."),
    ("h1", "3. Noise trader (semana 2)"),
    ("p", "O Miguel já fez o NoiseTrader com um Event. Fica assim: os noise traders continuam a enviar ordens durante a "
          "reserva (essas ordens esperam pelo leilão, como na realidade), por isso não precisam de statechart. A tua "
          "parte é afinar `noiseRate` e `noiseSigma` na calibração (secção 5)."),
    ("h1", "4. Chartist (tendência) com efeito manada (semana 3)"),
    ("p", "O chartist compra se o preço está acima da média móvel e vende se está abaixo. Quando vende, avisa os vizinhos "
          "na rede (`SELL_SIGNAL`). Se receber avisos de vizinhos suficientes, entra em pânico e vende muito: é a "
          "manada, como no Market Model."),
    ("ol", [
        "Parâmetros no Main: `nChartists` int 30, `chartRate` 0.2, `trendThreshold` 0.005, `herdThreshold` int 2, "
        "`panicDuration` 10, `shockPanicProb` 0.3, `shockSize` -0.10.",
        "População `chartists` (type `Chartist`, Initial number `nChartists`). Variáveis: `cash` 5000, `position` 10000, `sellSignals` int 0.",
        "Rede: Main → Properties → **Space and network** → Network type **Small world**, Connections per agent **6**, "
        "Neighbor link probability 0.95. A rede liga todos os agentes do Main; por isso o código confirma que o vizinho é um Chartist.",
        "Chartist → Properties → **Communication** (ou *Agent actions*) → **On message received**: "
        "`statechart.receiveMessage(msg);` Se já houver a opção *Forward message to: statechart* marcada, não escrevas nada, "
        "porque senão a mensagem chega duas vezes.",
        "Event `forget` (Cyclic, 30 min): `sellSignals = 0;` (esquece avisos antigos).",
        "Função **signalNeighbours** (Just action):",
    ]),
    ("code", """
for (Agent n : getConnections())
    if (n instanceof Chartist) send("SELL_SIGNAL", n);
"""),
    ("code", """
 +----------------------------------- Active -------------------------------------+
 |  Neutral --Rate chartRate--> <decide> --subida--> TrendBuy  --T0--> Neutral     |
 |                                  |-----descida--> TrendSell --T0--> Neutral     |
 |                                  '-----default--> Neutral                       |
 |  Neutral --"SELL_SIGNAL" (sellSignals++)--> <herd> --vizinhos>=limite--> Panic  |
 |                                               '------default----------> Neutral |
 |  Neutral --"SHOCK" (guard: prob.)---------------------------------------> Panic |
 |  Panic --Timeout panicDuration (sellSignals = 0)--> Neutral                     |
 +--------------------------------------------------------------------------------+
        "HALT" --> Halted --"REOPEN"--> Active
"""),
    ("table", [
        ["Transição", "Triggered by", "Condition / Guard / Action"],
        ["Neutral → decide", "Rate `main.chartRate`", "—"],
        ["decide → TrendBuy", "Condition", "`main.stock.lastPrice > main.stock.ma * (1 + main.trendThreshold) && cash > main.stock.mid() * 100`"],
        ["decide → TrendSell", "Condition", "`main.stock.lastPrice < main.stock.ma * (1 - main.trendThreshold) && position >= 100`"],
        ["decide → Neutral", "Default", "—"],
        ["TrendBuy/TrendSell → Neutral", "Timeout 0", "—"],
        ["Neutral → herd", "Message `\"SELL_SIGNAL\"`", "Action: `sellSignals++;`"],
        ["herd → Panic", "Condition", "`sellSignals >= main.herdThreshold && position > 0`"],
        ["herd → Neutral", "Default", "—"],
        ["Neutral → Panic", "Message `\"SHOCK\"`", "Guard: `main.shockSize < 0 && randomTrue(main.shockPanicProb)`"],
        ["Panic → Neutral", "Timeout `main.panicDuration`", "Action: `sellSignals = 0;`"],
        ["Active → Halted / Halted → Active", "Message `\"HALT\"` / `\"REOPEN\"`", "—"],
    ], [4.2, 3.6, 8.2]),
    ("code", """
// TrendBuy -> Entry action
double p = main.stock.mid() * 1.003;
int q = (int) Math.min(cash / p, 500);
if (q >= 100) main.stock.order(this, 1, p, q);

// TrendSell -> Entry action
main.stock.order(this, -1, main.stock.mid() * 0.997, Math.min(position, 500));
signalNeighbours();

// Panic -> Entry action (vende muito e abaixo do mercado)
if (position > 0) main.stock.order(this, -1, main.stock.mid() * 0.99, Math.min(position, 2000));
signalNeighbours();
"""),
    ("p", "A média móvel `main.stock.ma` é atualizada pelo Miguel a cada minuto. **Teste:** `nChartists = 60` e "
          "`herdThreshold = 1` devem dar quedas fortes; com `collarSet = 2` essas quedas devem abrir reservas. Commit e avisa."),
    ("h1", "5. Calibração com a Margarida (semana 4)"),
    ("ol", [
        "A Margarida corre o cenário baseline no AnyLogic (10 replicações). Os resultados ficam em `model/output/precos.csv`.",
        "Tu corres `python scripts/compare_model.py baseline`. O script mostra o BCP real vs. o modelo e se cada "
        "estatística **bate** (a menos de 25%). No modelo, um dia tem 510 minutos e o último preço de cada bloco conta como fecho.",
        "Se não bater, escolhem juntos o que mudar (tabela abaixo), ela corre outra vez e tu comparas outra vez. Muda uma "
        "coisa de cada vez e anota cada tentativa em `data/processed/calibracao_log.xlsx` (data, parâmetros, resultados): "
        "vai para o relatório.",
    ]),
    ("table", [
        ["Se no modelo…", "Experimenta…"],
        ["a volatilidade diária é baixa demais", "subir `noiseSigma`, subir `nChartists`, subir `fundBand`"],
        ["a volatilidade é alta demais", "o contrário; subir `nFundamentalists`"],
        ["a curtose (caudas pesadas) é baixa demais", "subir `nChartists`, descer `herdThreshold`, subir `panicDuration`"],
        ["há pouco clustering de volatilidade", "subir `chartRate`, subir `panicDuration`"],
        ["há dias com variação > 3% a mais", "subir `nFundamentalists` ou `fundRate`"],
        ["o preço afasta-se do valor e não volta", "subir `nFundamentalists`, `fundRate`"],
    ], [7, 9]),
    ("h2", "Validação (semana 4)"),
    ("ul", [
        "**ESMA:** a Margarida preenche a tabela da ESMA (efeitos das interrupções). No cenário 2 com colares, na folha "
        "**halts** do `kpis.xlsx`, `vol_depois` tem de ser menor que `vol_antes` e `spread_depois` maior que `spread_antes`.",
        "**BES:** compara a queda máxima do cenário 2 sem colares com a queda real do BCP no verão de 2014 (está na tua tabela de metas).",
    ]),
    ("h1", "6. KPIs dos cenários (semanas 3–6)"),
    ("p", "Sempre que a Margarida acabar um lote de corridas no AnyLogic, corres `python scripts/kpis.py`. Cria "
          "`data/processed/kpis.xlsx` com 3 folhas: **halts** (uma linha por interrupção), **runs** (uma por corrida) e "
          "**resumo** (média e intervalo de confiança de 95% por cenário)."),
    ("table", [
        ["KPI da proposta", "Onde está no kpis.xlsx"],
        ["Volatilidade antes vs. depois (2, 5, 10 min)", "halts: `vol_antes_w`, `vol_depois_w`"],
        ["Spread antes vs. depois", "halts: `spread_antes_w`, `spread_depois_w`"],
        ["Gap entre o preço do leilão e o preço antes", "halts: `gap_leilao`"],
        ["Queda máxima (maximum drawdown)", "runs/resumo: `queda_maxima`"],
        ["Volume e tempo sem negociação contínua", "runs/resumo: `volume_total`, `tempo_em_interrupcao`"],
        ["Tempo para recuperar metade da queda", "runs/resumo: `min_recuperar_metade`"],
        ["Interrupções repetidas", "runs/resumo: `n_interrupcoes`"],
        ["Curtose dos retornos", "runs/resumo: `curtose_ret_1min`"],
    ], [7.5, 8.5]),
    ("p", "Na semana 6 corres o `kpis.py` sobre as corridas finais e dás o `kpis.xlsx` à **Matilde**, que faz os gráficos."),
    ("h1", "7. Fase 2: MarketMaker em stress (semana 5)"),
    ("p", "O MarketMaker da Matilde cota sempre. Em stress, os criadores de mercado reais alargam o spread ou retiram-se. "
          "Tu acrescentas isso ao agente dela (pede-lhe o modelo, ou faz na tua cópia depois de integrado). Novos estados: "
          "**Wide** (spread × 3) e **Withdrawn** (sem cotações). Novo parâmetro `mmObligation` (boolean): se for true, o "
          "criador é obrigado a cotar com spread máximo `mmMaxSpread` (cenário 2 da Fase 2). Troca o Timeout 1 de Quoting por um Branch:"),
    ("code", """
 Quoting --Timeout 1--> <stress>
     stress > 0.04 && !main.mmObligation  --> Withdrawn (entry: main.stock.cancelAll(this);)
     stress > 0.02                        --> Wide      (entry: como quote() mas com spread * 3,
                                                         ou main.mmMaxSpread se mmObligation)
     default                              --> Quoting
 Withdrawn / Wide --Timeout 1--> <stress>
 onde stress = Math.abs(main.stock.lastPrice / main.stock.ma - 1)
"""),
    ("h1", "8. Semana 6: relatório"),
    ("ul", [
        "Investidores: os statecharts e as regras deste guião (fundamentalista, chartist e manada, criador de mercado em stress).",
        "Dados: de onde vêm, o que medem e a tabela de metas.",
        "Resultados: as tabelas do resumo do `kpis.xlsx`, com médias e intervalos de confiança.",
    ]),
]

# ----------------------------------------------------------------------------------------------
# Margarida
# ----------------------------------------------------------------------------------------------
MARGARIDA = [
    ("h1", "Resumo das tuas semanas"),
    ("table", [
        ["Semana", "Entrega concreta"],
        ["1 (17–24 out)", "Aprender as experiências do AnyLogic (Parameters Variation, Optimization); notas da ESMA."],
        ["2 (24–31 out)", "**Instrumentar o modelo**: parâmetros de cenário, ficheiros CSV de saída e KPIs (secção 2)."],
        ["3 (31 out–7 nov)", "Montar as experiências dos cenários e fazer as primeiras corridas (o João testa o `kpis.py` com elas)."],
        ["4 (7–14 nov)", "**Calibração** com o João: tu corres o baseline e mudas os parâmetros, ele compara com o BCP."],
        ["5 (14–21 nov)", "Correr os cenários da Fase 1 com 30 replicações. Fase 2: **LeveragedTrader**."],
        ["6 (21–28 nov)", "Corridas finais (grelha e otimização). Relatório: instrumentação, cenários e experiências, e "
                          "o investidor alavancado."],
    ], [3.2, 12.8]),
    ("h1", "1. Semana 1: experiências do AnyLogic e ESMA"),
    ("ol", [
        "Lê o capítulo 0 deste guião.",
        "No AnyLogic: Help → **AnyLogic Help** → lê as páginas “Parameter variation experiment” e “Optimization "
        "experiment”. Num modelo de teste qualquer, faz uma Parameters Variation com 1 parâmetro e 5 replicações, para "
        "ver como funciona. É isto que vais usar a partir da semana 3.",
        "Lê a secção 3 deste guião (cenários) para saberes o que vais correr.",
    ]),
    ("h2", "ESMA (2020)"),
    ("p", "Procura “ESMA Market impacts of circuit breakers 2020” (é um ESMA Economic Report). Lê o resumo e os resultados "
          "e preenche esta tabela em `sandbox/margarida/esma.md`. São as metas qualitativas da validação:"),
    ("table", [
        ["Efeito", "O que a ESMA encontrou (sentido e número)", "Página"],
        ["volatilidade depois vs. antes da interrupção", "", ""],
        ["spread depois vs. antes", "", ""],
        ["volume depois vs. antes", "", ""],
        ["preço do leilão vs. preço antes (continua a cair ou recupera?)", "", ""],
        ["frequência de interrupções repetidas", "", ""],
    ], [6.5, 7.5, 2]),
    ("p", "Dá a tabela ao João: ele usa-a na validação."),
    ("h1", "2. Semana 2: instrumentar o modelo (cenários, CSV e KPIs)"),
    ("p", "És tu que vais usar os dados que o modelo produz, por isso és tu que defines o que ele grava. Fazes isto "
          "no Main da tua cópia (`sandbox/margarida/margarida.alp`, copiada do modelo base do Miguel) e, no fim, o "
          "Miguel copia para o modelo principal. Também te serve de treino de AnyLogic para as experiências."),
    ("ol", [
        "Cria a pasta `sandbox/margarida/output/`. Quando o Miguel integrar, a pasta passa a ser `model/output/`.",
        "No Main, **parâmetros** (Palette → Agent → Parameter): `collarSet` int 2, `customDyn` 0.03, `customStat` 0.08, "
        "`scenario` String \"baseline\".",
        "**Variáveis**: `label` String, `runId` String com Initial value "
        "`java.util.UUID.randomUUID().toString().substring(0, 8)`, `peakPrice` double, `maxDrawdown` double 0, "
        "`nHalts` int 0, `timeHalted` double 0.",
        "Palette **Connectivity** → **Text File**: name `pricesFile`, File `output/precos.csv`, Mode **Append**. "
        "Outro igual: `haltsFile`, `output/halts.csv`.",
        "Main → Properties → Agent actions → **On startup**:",
    ]),
    ("code", """
switch (collarSet) {
    case 0: collarsActive = false; break;                                      // sem colares
    case 1: dynamicThreshold = 0.02; staticThreshold = 0.05; break;
    case 2: dynamicThreshold = 0.03; staticThreshold = 0.08; break;            // regras atuais
    case 3: dynamicThreshold = 0.05; staticThreshold = 0.10; break;
    case 4: dynamicThreshold = customDyn; staticThreshold = customStat; break; // otimização
}
peakPrice = initialPrice;
label = scenario + "_c" + collarSet + "_h" + haltShort;   // quando entrar o Chartist: + "_n" + nChartists
"""),
    ("ol", [
        "Event `logEvent` no Main: Mode *Cyclic*, First occurrence 1, Recurrence 1. Action:",
    ]),
    ("code", """
double p = stock.lastPrice;
peakPrice = Math.max(peakPrice, p);
maxDrawdown = Math.max(maxDrawdown, 1 - p / peakPrice);
pricesFile.println(label + ";" + runId + ";" + time() + ";" + p + ";"
                   + stock.bestBid() + ";" + stock.bestAsk() + ";" + stock.volume);
"""),
    ("ol", [
        "Main → **On destroy**: `pricesFile.close(); haltsFile.close();`",
        "No Stock, nas funções `startHalt` e `endHalt` do Miguel, descomenta as linhas com `main.nHalts`, "
        "`main.haltsFile`, `main.label`, `main.runId` e `main.timeHalted`.",
        "**Teste:** corre a Simulation durante uns minutos e fecha. O `output/precos.csv` deve ter linhas como "
        "`baseline_c2_h3.0;a1b2c3d4;12.0;0.5013;0.501;0.5016;84200`. Com `noiseSigma = 0.01` devem aparecer linhas no `halts.csv`.",
        "Commit e avisa o Miguel para integrar (ele tem os passos no guião dele, secção 6).",
    ]),
    ("h1", "3. Correr o modelo e os cenários no AnyLogic (semanas 3–5)"),
    ("h2", "Onde saem os dados"),
    ("p", "Cada corrida acrescenta linhas a `model/output/precos.csv` (um preço por minuto) e `model/output/halts.csv` "
          "(uma linha por interrupção). **Antes de cada lote de corridas apaga estes dois ficheiros**, para não misturar "
          "com corridas antigas. Cada linha tem um `label` (cenário mais parâmetros) e um `run` (a corrida)."),
    ("h2", "Cenários da Fase 1 (da proposta)"),
    ("table", [
        ["#", "Cenário", "scenario", "shockOn", "collarSet", "nChartists", "haltShort", "Stop time"],
        ["1", "Baseline: calibração e validação", "baseline", "false", "2", "30", "3", "127500 (250 dias)"],
        ["2", "Choque grande com e sem colares (BES)", "shock", "true", "2 e 0", "30", "3", "61200"],
        ["3", "Choque com muitos chartists (março 2020)", "herd", "true", "2 e 0", "60", "3", "61200"],
        ["4", "Grelha de colares × duração", "grid", "true", "0, 1, 2, 3", "30", "3 e 10", "61200"],
    ], [0.6, 4.6, 1.6, 1.4, 1.7, 1.7, 1.6, 2.8]),
    ("p", "`collarSet`: 0 = sem colares, 1 = 2%/5%, 2 = 3%/8% (atual), 3 = 5%/10%. O choque (`shockSize` = −10%) acontece no dia 60 (`shockTime` = 30600)."),
    ("h2", "Criar uma experiência de cenários (Parameters Variation)"),
    ("ol", [
        "Projects → botão direito em `Euronext_Main` → **New → Experiment → Parameters Variation** → Name `Cenario2` → Finish.",
        "Propriedades → **Parameters**: para cada parâmetro escolhe **Fixed** (um valor), **Range** (Min, Max, Step) ou "
        "**Freeform** (uma lista de valores). Cenário 2: `scenario` = \"shock\", `shockOn` = true, `collarSet` Freeform 0 e 2.",
        "**Replications**: marca *Use replications* e *Fixed number of replications* = **30** (Monte Carlo).",
        "**Randomness**: *Fixed seed*. Assim o “com colares” e o “sem colares” usam as mesmas sementes: é o mesmo choque "
        "com a mesma sorte, como promete a proposta.",
        "**Model time**: Stop at specified time = 61200.",
        "Em **Advanced**, desmarca **Allow parallel evaluations** (duas corridas a escrever ao mesmo tempo no mesmo CSV estragam o ficheiro).",
        "Run (não há animação, espera que acabe). Os CSV de `model/output/` não vão para o GitHub, porque são grandes. "
        "Avisa o João, que corre o `kpis.py` e faz o `kpis.xlsx` (vê a dica abaixo).",
    ]),
    ("h2", "Grelha (cenário 4 e pergunta 1 da proposta)"),
    ("p", "Parameters Variation com `collarSet` Range 0–3 (step 1), `haltShort` Freeform 3 e 10, e `nChartists` Range "
          "10–60 (step 10). São 4 × 2 × 6 = 48 combinações; com 30 replicações dá 1440 corridas. Começa com 5 replicações "
          "para ver quanto tempo demora."),
    ("h2", "Otimização (os limiares que minimizam a queda)"),
    ("ol", [
        "New → Experiment → **Optimization**. Objective: **minimize** `root.maxDrawdown`.",
        "Parameters: `collarSet` Fixed 4; `customDyn` *continuous* 0.01–0.06; `customStat` *continuous* 0.04–0.15; `shockOn` true.",
        "Replications: 10 por iteração.",
        "**Requirements**: expressão `root.stock.volume`, lower bound = 90% do volume médio do cenário 2 com colares "
        "(está no kpis.xlsx). É o “sem perder demasiada liquidez”.",
        "Number of iterations 200 → Run. A melhor combinação aparece na tabela da experiência.",
    ]),
    ("tip", "Para não andarem a passar CSV de um lado para o outro, o mais simples é o João correr o `kpis.py` e o "
            "`compare_model.py` no teu PC: ele instala o Python lá uma vez, ou fazem-no juntos numa chamada."),
    ("h1", "4. Calibração com o João (semana 4)"),
    ("ol", [
        "Apaga os CSV de `model/output/` e corre o cenário 1 (baseline) com 10 replicações e Stop 127500.",
        "O João compara com o BCP real (`compare_model.py`) e diz-te o que não bate.",
        "Escolhem juntos o que mudar (a tabela de afinação está no guião dele, secção 5). Tu mudas os parâmetros no "
        "AnyLogic e corres outra vez. Muda uma coisa de cada vez.",
    ]),
    ("h1", "5. Fase 2: LeveragedTrader (semana 5)"),
    ("p", "Investidor com dinheiro emprestado. Se o preço cai, vende por stop-loss; se a margem fica abaixo do mínimo, "
          "recebe uma chamada de margem (margin call) e é obrigado a vender. É isto que cria as cascatas da pergunta 3. "
          "Faz na tua cópia e avisa o Miguel para integrar."),
    ("ol", [
        "Parâmetros no Main: `nLeveraged` 10, `leverage` 3, `stopLoss` 0.05, `maintenanceMargin` 0.25.",
        "População `leveraged` (type `LeveragedTrader`, Initial number `nLeveraged`). Variáveis: `cash` 5000 (capital "
        "próprio), `loan` 0, `position` 0, `entryPrice` 0.",
        "Função **margin** (Returns double): `double v = position * main.stock.mid(); return v > 0 ? (v - loan) / v : 1;`",
        "Statechart (as regras de como desenhar estão no capítulo 0; os do João são um bom exemplo):",
    ]),
    ("code", """
 Normal --Rate 0.05--> Open (entry: compra alavancado) --T0--> Holding
 Holding --Rate 1--> <check> --preço < entry*(1-stopLoss)----> StopLoss   (entry: vende tudo a mid*0.995)
                        |-----margin() < maintenanceMargin---> MarginAlert --Timeout 5--> <again>
                        '-----default------------------------> Holding        |--margem ainda baixa--> ForcedSale
 StopLoss / ForcedSale --T0--> Normal  (ou Liquidated se cash <= 0)            '--default------------> Holding
"""),
    ("code", """
// Open -> Entry action
double p = main.stock.mid() * 1.002;
int q = (int) (cash * main.leverage / p);
loan = cash * (main.leverage - 1);
entryPrice = p;
main.brokers.get(0).order(this, 1, p, q);     // as ordens passam pelo broker da Matilde

// MarginAlert -> Entry action (avisa o broker)
send("MARGIN_CALL", main.brokers.get(0));

// ForcedSale -> Entry action (vende tudo, muito abaixo do mercado)
main.brokers.get(0).order(this, -1, main.stock.mid() * 0.98, position);
"""),
    ("p", "Enquanto o broker da Matilde não estiver pronto, usa `main.stock.order(...)` em vez de `main.brokers.get(0).order(...)`."),
    ("h1", "6. Semana 6"),
    ("ul", [
        "Corridas finais: cenários com 30 replicações, a grelha e a otimização. Avisa o João para fazer o `kpis.xlsx` final.",
        "Relatório: como o modelo é instrumentado (que dados grava), os cenários e as experiências (Parameters Variation, "
        "replicações, sementes fixas, otimização) e o investidor alavancado.",
    ]),
]

# ----------------------------------------------------------------------------------------------
# Matilde
# ----------------------------------------------------------------------------------------------
MATILDE = [
    ("h1", "Resumo das tuas semanas"),
    ("table", [
        ["Semana", "Entrega concreta"],
        ["1 (17–24 out)", "Tutorial de gráficos e controlos; esboço do ecrã inicial e do dashboard; statecharts em papel. "
                          "Quando o modelo base sair: começar o NewsAgent."],
        ["2 (24–31 out)", "**NewsAgent e MarketMaker a funcionar.** Commit e avisar."],
        ["3 (31 out–7 nov)", "Ecrã inicial (sliders) e cores dos agentes por estado."],
        ["4 (7–14 nov)", "**Dashboard final.**"],
        ["5 (14–21 nov)", "Fase 2: **Broker completo** (fila + dois statecharts)."],
        ["6 (21–28 nov)", "**Gráficos finais** (a partir do kpis.xlsx do João), apresentação e a tua parte do relatório "
                          "(interface, criador de mercado, notícias, broker)."],
    ], [3.2, 12.8]),
    ("h1", "1. Semana 1"),
    ("ol", [
        "Tutorial (~2 h): no AnyLogic, Help → **AnyLogic Help** → procura “Time Plot”, “Bar Chart”, “Slider” e "
        "“Radio buttons”. Em cada página, faz o exemplo num modelo de teste qualquer.",
        "Em papel: ecrã inicial e dashboard (esboço abaixo; podes melhorar).",
        "Lê o capítulo 0 e desenha em papel os statecharts do NewsAgent e do MarketMaker (secções 2 e 3).",
        "Quando o Miguel publicar o modelo base: Pull → copia `model/Euronext_Main.alp` para `sandbox/matilde/matilde.alp` → abre esse.",
    ]),
    ("plan_b", "matilde"),
    ("code", """
 ECRÃ INICIAL (experiência Simulation)          DASHBOARD (Main)
 +--------------------------------------+       +---------------------------+------------------+
 | Fundamentalistas [=====|----]   40   |       | Preço vs valor fundamental| Estado: CONTÍNUO |
 | Tendência        [===|------]   30   |       | (time plot)               | Interrupções: 3  |
 | Ruído            [===|------]   30   |       |                           | Queda máx: 12.4% |
 | Colares ( ) nenhum ( ) 2/5 (x) 3/8   |       +---------------------------+ Volume: 1.2M     |
 |         ( ) 5/10                     |       | Spread (time plot)        +------------------+
 | Pausa [ 3] min   Pausa longa [10] min|       |                           | Livro: compras / |
 | Choque [x]   tamanho [==|-----] -10% |       +---------------------------+ vendas (barras)  |
 |               [ RUN ]                |       | Histograma de retornos    | Agentes (cor =   |
 +--------------------------------------+       |                           |  estado)         |
                                                +---------------------------+------------------+
"""),
    ("h1", "2. NewsAgent: notícias e choques (semana 2)"),
    ("p", "Gera a informação externa. Em geral está calmo e de vez em quando há pequenas notícias. No cenário de choque, "
          "no dia 60, o valor fundamental cai (ex.: −10%, como o BES) e todos são avisados com `SHOCK`; segue-se uma fase "
          "de dissipação com pequenas réplicas."),
    ("ol", [
        "Parâmetros no Main: `shockOn` boolean false, `shockTime` 30600, `shockSize` -0.10, `newsRate` 0.0004.",
        "Palette → Agent → **Agent** → **Single agent** → type `NewsAgent`, name `news`.",
        "Event `shockEvent`: Trigger *Timeout*, Mode **Occurs once**, Occurrence time `main.shockTime`. Action: "
        "`if (main.shockOn) statechart.receiveMessage(\"BIG_SHOCK\");`",
    ]),
    ("code", """
 Calm --Rate newsRate--> SmallNews --T0--> Calm
 Calm --Message "BIG_SHOCK"--> BigShock --Timeout 30--> Fading --Timeout 120--> Calm
                                                       Fading --Rate 0.05--> Fading  (réplicas)
"""),
    ("code", """
// SmallNews -> Entry action (notícia pequena, boa ou má)
main.fundamentalValue *= 1 + normal(0.01, 0);

// BigShock -> Entry action
main.fundamentalValue *= 1 + main.shockSize;
main.broadcast("SHOCK");
traceln("CHOQUE em t=" + time());

// Fading -> Fading (transição para o próprio estado, Rate 0.05) -> Action
main.fundamentalValue *= 1 + normal(0.005, -0.003);     // pequenas réplicas, em média negativas
"""),
    ("p", "**Teste:** `shockOn = true` e `shockTime = 600`. Ao minuto 600 deve aparecer “CHOQUE” na consola e o "
          "`fundamentalValue` deve cair no gráfico (os fundamentalistas do João arrastam depois o preço)."),
    ("h1", "3. MarketMaker: criador de mercado (semana 2)"),
    ("p", "Dá liquidez: põe sempre uma compra um pouco abaixo e uma venda um pouco acima do preço médio e atualiza-as a "
          "cada minuto. Durante a reserva retira as ordens."),
    ("ol", [
        "Parâmetros no Main: `mmSpread` 0.004, `mmQty` int 2000.",
        "**Single agent** → type `MarketMaker`, name `marketMaker`. Variáveis: `cash` double 0, `position` int 0.",
        "Função **quote** (Just action):",
    ]),
    ("code", """
main.stock.cancelAll(this);                    // tira as cotações antigas
double m = main.stock.mid();
main.stock.order(this, 1, m * (1 - main.mmSpread / 2), main.mmQty);
main.stock.order(this, -1, m * (1 + main.mmSpread / 2), main.mmQty);
"""),
    ("code", """
 Quoting (entry: quote();) --Timeout 1--> Quoting      (seta do estado para ele próprio)
 Quoting --Message "HALT"--> Paused (entry: main.stock.cancelAll(this);) --Message "REOPEN"--> Quoting
"""),
    ("p", "A seta de Quoting para Quoting: com a Transition em modo de desenho, clica na borda de Quoting e outra vez "
          "noutro ponto da borda de Quoting. Ao re-entrar, o Entry action corre de novo, por isso volta a cotar a cada minuto."),
    ("h1", "4. Ecrã inicial (semana 3)"),
    ("ol", [
        "Projects → `Simulation` → Properties → botão **Create default UI**. O AnyLogic cria um controlo para cada parâmetro, já ligado.",
        "Apaga os que não interessam ao utilizador. Ficam: `nFundamentalists`, `nChartists`, `nNoise` (Slider 0–100), "
        "`collarSet`, `haltShort`, `haltLong` (Edit box), `shockOn` (Check box), `shockSize` (Slider −0.30 a 0).",
        "Para `collarSet` apaga o controlo criado e põe um **Radio Buttons** (Palette Controls) com 4 opções: "
        "“Sem colares”, “2% / 5%”, “3% / 8% (atual)”, “5% / 10%”. Em **Link to** escolhe o parâmetro `collarSet`: a "
        "1.ª opção vale 0, a 2.ª vale 1, etc.",
        "Título, logótipo da FEUP (Palette Presentation → **Image**) e uma frase a explicar o modelo.",
    ]),
    ("h1", "5. Dashboard (semanas 3–4)"),
    ("p", "Faz no Main da tua cópia; depois o Miguel copia os elementos para o modelo principal (copiar e colar formas entre modelos funciona)."),
    ("table", [
        ["Elemento", "Palette", "O que pôr"],
        ["Preço", "Analysis → Time Plot", "Values `stock.lastPrice` (“Preço”) e `fundamentalValue` (“Valor fundamental”); Time window 510"],
        ["Spread", "Analysis → Time Plot", "Value `stock.spread()`"],
        ["Livro de ordens", "Analysis → Bar Chart", "Values `stock.bidBook.size()` (“Compras”) e `stock.askBook.size()` (“Vendas”)"],
        ["KPIs", "Presentation → Text", "Text dinâmico (clica no ícone = ao lado do campo): `\"Estado: \" + (stock.halted ? \"RESERVA\" : \"CONTÍNUO\")`, "
                                       "`\"Interrupções: \" + nHalts`, `String.format(\"Queda máxima: %.1f%%\", 100 * maxDrawdown)`, `\"Volume: \" + stock.volume`"],
        ["Retornos", "Analysis → Histogram Data + Histogram", "Histogram Data `retData` (40 intervalos); Histogram com Data `retData`"],
    ], [2.6, 4.4, 9.0]),
    ("p", "Para o histograma: variável `prevPrice` no Main (Initial value `initialPrice`) e um Event `retEvent` (Cyclic, 1 min):"),
    ("code", """
retData.add(Math.log(stock.lastPrice / prevPrice));
prevPrice = stock.lastPrice;
"""),
    ("h2", "Cores dos agentes por estado"),
    ("ol", [
        "Main → Properties → **Space and network** → Layout type *Random*.",
        "Abre o tipo `Fundamentalist` (do João) → Palette Presentation → **Oval** pequeno no centro → Fill color → "
        "dinâmico: `inState(Buying) ? green : inState(Selling) ? red : inState(Halted) ? gray : silver`",
        "Igual no `Chartist`: `inState(Panic) ? red : inState(TrendSell) ? orange : inState(TrendBuy) ? green : silver`",
        "Durante a simulação, o livro de ordens anima-se sozinho: escolhe `stock` na barra de cima e vês as filas a encher e a esvaziar.",
    ]),
    ("h1", "6. Fase 2: Broker (semana 5)"),
    ("p", "O MarketMaker em stress (Fase 2) fica com o João: ele acrescenta estados ao teu agente."),
    ("h2", "Broker, parte 1: a fila (Process Modeling Library)"),
    ("p", "O broker recebe as ordens dos investidores alavancados, põe-nas numa fila com capacidade limitada e envia-as "
          "para o mercado. Se a plataforma estiver sobrecarregada, rejeita ordens. É a “fila do broker” da proposta."),
    ("ol", [
        "Parâmetros no Main: `brokerRate` 2 (ordens processadas por minuto, por servidor), `brokerServers` int 1, "
        "`graceMinutes` 15.",
        "Palette → Agent → **Agent** → **Population of agents** → type `Broker`, population `brokers`, Initial number 1. "
        "Parâmetro do Broker: `capacity` int 50. Variáveis: `accepting` boolean true, `rejectedCount` int 0.",
        "Dentro do Broker, desenha com a Process Modeling Library:",
    ]),
    ("code", """
 brokerIn --> tmStart --> accept --(true)--> brokerQueue --> processing --> tmEnd --> toMarket
                            '--(false)--> rejected (Sink)
"""),
    ("table", [
        ["Bloco", "Tipo", "Propriedades (em todos: Agent type `Order`)"],
        ["brokerIn", "Enter", "—"],
        ["tmStart / tmEnd", "TimeMeasureStart / TimeMeasureEnd", "no tmEnd, TimeMeasureStart: `tmStart`. O KPI do tempo de espera é `tmEnd.distribution.mean()`"],
        ["accept", "SelectOutput", "Condition `accepting && brokerQueue.size() < capacity`"],
        ["brokerQueue", "Queue", "Maximum capacity"],
        ["processing", "Delay", "Delay time `exponential(main.brokerRate)`; Capacity `main.brokerServers`"],
        ["toMarket", "Exit", "On exit: `main.stock.enter.take(agent);`"],
        ["rejected", "Sink", "On enter: `rejectedCount++;`"],
    ], [3.0, 4.4, 8.6]),
    ("p", "Função **order** do Broker (Just action; argumentos `trader` Agent, `side` int, `price` double, `qty` int). "
          "É igual à do Stock, mas a ordem entra no broker:"),
    ("code", """
Order o = new Order();
o.id = main.nextOrderId++;
o.side = side;
o.price = main.roundTick(price);
o.qty = qty;
o.tSubmit = time();
o.trader = trader;
brokerIn.take(o);
"""),
    ("p", "**Teste:** põe `capacity = 5` e `brokerRate = 0.2`: o `rejectedCount` deve subir e a fila deve encher na animação."),
    ("h2", "Broker, parte 2: dois statecharts em paralelo"),
    ("p", "No mesmo agente `Broker` põe **dois** Statechart Entry Points: `riskChart` e `platformChart`. O "
          "`platformChart` liga e desliga a variável `accepting` que a fila usa."),
    ("code", """
 platformChart:  Operational --Timeout 1--> <load>
                    brokerQueue.size() > 0.95 * capacity --> Rejecting   (entry: accepting = false;)
                    brokerQueue.size() > 0.70 * capacity --> Overloaded  (entry: accepting = true;)
                    default                              --> Operational (entry: accepting = true;)
                 Overloaded / Rejecting --Timeout 1--> <load>

 riskChart:      Normal --Message "MARGIN_CALL"--> MarginAlert --Timeout main.graceMinutes--> ForcedLiquidation
                 ForcedLiquidation (entry: manda "LIQUIDATE" aos clientes) --Timeout 30--> Normal
"""),
    ("p", "`graceMinutes` é o “regras de margem apertadas vs. folgadas” da proposta (ex.: 5 vs. 60 min). O "
          "LeveragedTrader da Margarida manda `MARGIN_CALL` ao broker quando entra em MarginAlert. Para a mensagem chegar "
          "ao statechart certo: Broker → Properties → **On message received**: `riskChart.receiveMessage(msg);`"),
    ("h1", "7. Semana 6: gráficos finais"),
    ("p", "O João dá-te o `data/processed/kpis.xlsx` final. Fazes estes gráficos, que vão para o relatório e para a apresentação:"),
    ("ul", [
        "Preço com e sem colares no mesmo choque (mesma semente): mostra o efeito da interrupção. Corre a Simulation "
        "duas vezes com `collarSet` 2 e 0 e exporta o Time Plot (botão direito → Copy all → Excel).",
        "Boxplot da queda máxima por `collarSet` (folha **runs**, 30 replicações cada).",
        "**Trade-off estabilidade vs. liquidez**: queda máxima (eixo x) contra volume ou tempo em interrupção (eixo y), "
        "um ponto por combinação da grelha (folha **resumo**). É a figura central da proposta.",
        "Volatilidade e spread antes e depois, a 2, 5 e 10 min (folha **halts**): gráfico de barras.",
        "Podes fazê-los em Excel, ou pedir ao Claude Code um script Python que os faça todos a partir do kpis.xlsx.",
    ]),
    ("h1", "8. Semana 6: apresentação"),
    ("ul", [
        "Estrutura sugerida (10–12 slides): problema (PSI, BES 2014, março 2020) → colares da Euronext → livro de ordens "
        "como fila → agentes (um slide com os statecharts) → dados e calibração (tabela BCP real vs. modelo) → "
        "cenários → resultados (o trade-off) → conclusões e limitações.",
        "Uma demonstração ao vivo de 1 minuto do dashboard com o choque ligado costuma resultar muito bem.",
    ]),
]

PEOPLE = [
    ("Miguel", "miguel", "Motor do mercado (livro de ordens, colares, leilão) e integração", MIGUEL),
    ("João", "joao", "Investidores (fundamentalista, tendência/manada, criador de mercado em stress) e dados/Python (BCP, calibração, KPIs)", JOAO),
    ("Margarida", "margarida", "Experiências no AnyLogic (instrumentação, cenários, otimização), ESMA e investidor alavancado", MARGARIDA),
    ("Matilde", "matilde", "Notícias, criador de mercado, broker, ecrã inicial, dashboard e gráficos finais", MATILDE),
]


def build(nome, pasta, papel, blocks):
    path = OUT / f"Guiao_{pasta.capitalize()}.pdf"
    story = [Paragraph(f"Guião · {nome}", T), Paragraph(papel, SUB),
             Paragraph(fmt("SAD · Grupo 2 · Volatility Interruptions and Crash Contagion in Euronext Lisbon · "
                           "entrega a 2 de dezembro. Os nomes vêm de `docs/CONTRATO.md`."), N)]
    story += render(blocks[:2])            # resumo das semanas logo na 1.ª página
    story.append(PageBreak())
    story += render(common(pasta))
    story += render(blocks[2:])

    def foot(c, d):
        c.setFont("Ar", 8)
        c.setFillColor(colors.grey)
        c.drawString(2.5 * cm, 1.2 * cm, f"SAD · Grupo 2 · Guião {nome}")
        c.drawRightString(18.5 * cm, 1.2 * cm, str(d.page))

    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm, topMargin=2 * cm,
                      bottomMargin=2 * cm, title=f"Guião {nome} - SAD Grupo 2").build(story, onFirstPage=foot,
                                                                                      onLaterPages=foot)
    return path


def build_geral():
    """Resumo para o grupo: papéis, marcos e as tabelas semanais de cada pessoa (as mesmas dos guiões)."""
    path = OUT / "Guiao_Geral.pdf"
    story = [Paragraph("Guião de tarefas · Grupo 2", T),
             Paragraph("SAD · Volatility Interruptions and Crash Contagion in Euronext Lisbon · entrega a 2 de dezembro", SUB)]
    story += render([
        ("table", [["Pessoa", "Papel"]] + [[n, p] for n, _, p, _ in PEOPLE], [3.2, 12.8]),
        ("h1", "Marcos do grupo"),
        ("ul", [
            "**Domingo:** reunião de 30 min (todos) para confirmar os papéis e o `docs/CONTRATO.md`.",
            "**Quinta, 23 out:** modelo base do Miguel no GitHub (o preço mexe). Se atrasar, o João e a Matilde seguem o plano B do guião deles.",
            "**7 nov:** Fase 1 completa a correr.",
            "**14 nov:** decisão. Se a Fase 1 estiver validada, avança-se para a Fase 2; se não, polir.",
            "**21–28 nov:** cada um escreve a sua parte do relatório.",
            "**28 nov–2 dez:** revisão final de todos e entrega.",
        ]),
    ])
    for nome, _, _, blocks in PEOPLE:
        story += render([("h1", nome), blocks[1]])

    def foot(c, d):
        c.setFont("Ar", 8)
        c.setFillColor(colors.grey)
        c.drawString(2.5 * cm, 1.2 * cm, "SAD · Grupo 2 · Guião geral")
        c.drawRightString(18.5 * cm, 1.2 * cm, str(d.page))

    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm, topMargin=2 * cm,
                      bottomMargin=2 * cm, title="Guião geral - SAD Grupo 2").build(story, onFirstPage=foot,
                                                                                  onLaterPages=foot)
    return path


if __name__ == "__main__":
    for nome, pasta, papel, blocks in PEOPLE:
        print(build(nome, pasta, papel, blocks))
    print(build_geral())
