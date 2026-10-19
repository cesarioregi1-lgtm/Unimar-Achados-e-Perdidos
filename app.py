import base64
import datetime
from io import BytesIO
import random
import qrcode
import streamlit as st

# ---------------------------------------------------------
# 0. CONVERSÃO DA IMAGEM LOCAL PARA BASE64 (PLANO DE FUNDO UNIMAR)
# ---------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ''

img_path = '1001217215.jpg'
bin_str = get_base64_of_bin_file(img_path)

bg_css = (
    f'url("data:image/jpeg;base64,{bin_str}")'
    if bin_str
    else "linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.95))"
)

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Unimar - Achados e Perdidos", page_icon="🚌", layout="wide"
)

st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }}
    
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.92)), 
                    {bg_css};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    html, body, [class*="css"], div, p, span, label {{
        font-family: -apple-system, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, 'Segoe UI', sans-serif !important;
        color: #FFFFFF !important;
    }}

    h1, h2, h3, .stApp h1, .stApp h2, .stApp h3 {{
        color: #4DA8DA !important;
        font-weight: 700 !important;
    }}

    div[data-baseweb="input"] input, 
    div[data-baseweb="textarea"] textarea, 
    div[data-baseweb="select"] div,
    input, textarea, select {{
        color: #000000 !important;
        background-color: #FFFFFF !important;
        font-weight: 500 !important;
    }}

    input::placeholder, textarea::placeholder {{
        color: #666666 !important;
    }}

    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stDateInput > label {{
        color: #4DA8DA !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stColumn"] > div {{
        background-color: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(77, 168, 218, 0.3);
        border-radius: 14px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}

    div[data-testid="stColumn"] p, div[data-testid="stColumn"] span, div[data-testid="stColumn"] label {{
        color: #FFFFFF !important;
    }}

    .stButton>button {{
        border-radius: 8px;
        font-weight: 600;
        background-color: #1D61B0 !important;
        color: #FFFFFF !important;
        border: none !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.98) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}

    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {{
        color: #FFFFFF !important;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. CABEÇALHO COM LOGOTIPO SEGURO
# ---------------------------------------------------------
def render_logo_header():
    st.markdown(
        """
        <div style="text-align: center; margin-top: 5px; margin-bottom: 20px;">
            <h1 style="color: #4DA8DA; font-size: 2.5rem; margin-bottom: 0;">🚌 UNIMAR</h1>
            <p style="color: #94A3B8; font-size: 1.1rem; letter-spacing: 2px; margin-top: 0;">SISTEMA DE ACHADOS E PERDIDOS</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# 3. FUNÇÃO AUXILIAR PARA GERAR QR CODE
# ---------------------------------------------------------
def gerar_qrcode_bytes(texto):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# ---------------------------------------------------------
# 4. BASE DE DADOS (SESSION STATE) & CONTROLE DE AUTENTICAÇÃO
# ---------------------------------------------------------
if "banco_objetos" not in st.session_state:
    st.session_state.banco_objetos = [
        {
            "codigo": "UNI-8492",
            "descricao": "Mochila preta Targus com notebook",
            "linha": "Rota Industrial / Vale",
            "localizacao": "Garagem Unimar",
            "data_registro": "01/10/2026",
            "status": "Disponível",
            "foto_item": None,
            "dados_agendamento": None,
            "dados_entrega": None,
        }
    ]

if "alertas_perda" not in st.session_state:
    st.session_state.alertas_perda = []

if "solicitacoes_resgate" not in st.session_state:
    st.session_state.solicitacoes_resgate = []

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# ---------------------------------------------------------
# 5. NAVEGAÇÃO LATERAL
# ---------------------------------------------------------
st.sidebar.markdown("### 🚌 Unimar Transportes")
perfil_acesso = st.sidebar.radio(
    "Selecione o Modo de Visualização:",
    ["📱 Tela do Passageiro", "⚙️ Painel do Administrador"],
    key="perfil_acesso_radio",
)

st.sidebar.markdown("---")

if perfil_acesso == "⚙️ Painel do Administrador":
    if not st.session_state.admin_logado:
        st.sidebar.markdown("### 🔐 Acesso Restrito")
        senha_digitada = st.sidebar.text_input(
            "Senha do Administrador:", type="password"
        )
        if st.sidebar.button("Entrar no Painel"):
            if senha_digitada == "unimar2026":
                st.session_state.admin_logado = True
                st.success("Login efetuado com sucesso!")
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.sidebar.success("🟢 Sessão Administrativa Ativa")
        if st.sidebar.button("🚪 Logout (Sair)"):
            st.session_state.admin_logado = False
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("📌 Projeto de Extensão - Achados e Perdidos")

# =========================================================
# TELA DO PASSAGEIRO
# =========================================================
if perfil_acesso == "📱 Tela do Passageiro":
    render_logo_header()

    st.write(
        "Esqueceu algum pertence nos veículos da frota? Pesquise abaixo ou"
        " cadastre uma solicitação de busca."
    )
    st.markdown("---")

    col_busca, col_solicitar = st.columns([2, 1])

    with col_busca:
        st.markdown("### 🔎 Buscar Item Encontrado")
        termo_busca = st.text_input(
            "Digite o nome do objeto, linha do ônibus ou palavra-chave:",
            placeholder="Ex: Mochila, Chave, Garrafa, Linha Vale...",
        )

        itens_disponiveis = [
            i
            for i in st.session_state.banco_objetos
            if i["status"] in ["Disponível", "Agendado"]
        ]

        if termo_busca:
            resultados = [
                i
                for i in itens_disponiveis
                if termo_busca.lower() in i["descricao"].lower()
                or termo_busca.lower() in i.get("linha", "").lower()
                or termo_busca.lower() in i["codigo"].lower()
            ]
        else:
            resultados = itens_disponiveis

        st.markdown(f"Itens Encontrados e Guardados ({len(resultados)}):")

        if not resultados:
            st.info("Nenhum pertence encontrado com a palavra pesquisada.")
        else:
            for item in resultados:
                tag_expander = f"📌 {item['codigo']} — {item['descricao']}"
                if item["status"] == "Agendado":
                    tag_expander += " (🟡 Agendado para Retirada)"

                with st.expander(tag_expander):
                    st.write(f"🚌 Linha/Rota: {item.get('linha', 'Frota Geral')}")
                    st.write(f"📍 Local de Retirada: {item['localizacao']}")
                    st.write(f"📅 Data de Entrada: {item.get('data_registro', 'Recente')}")

                    if item.get("foto_item"):
                        st.image(
                            item["foto_item"],
                            caption="Foto do Objeto Encontrado",
                            use_container_width=True,
                        )

                    st.markdown("---")

                    if item["status"] == "Agendado":
                        st.warning(
                            "🟡 Este item já possui um agendamento de retirada em andamento."
                        )
                        if item.get("dados_agendamento"):
                            st.write(f"👤 Solicitante: {item['dados_agendamento']['nome']}")
                    else:
                        st.write(
                            "É o seu pertence? Solicite a retirada preenchendo os dados abaixo:"
                        )

                        with st.form(key=f"form_resgate_{item['codigo']}"):
                            nome_p = st.text_input("Seu Nome Completo:")
                            contato_p = st.text_input("Telefone/WhatsApp para contato:")
                            detalhe_p = st.text_area(
                                "Descreva detalhes/marcas do item para confirmação:"
                            )

                            btn_solicitar = st.form_submit_button(
                                "📩 Solicitar Agendamento de Retirada"
                            )

                            if btn_solicitar:
                                if not nome_p or not contato_p:
                                    st.error(
                                        "Por favor, preencha seu nome e telefone de contato."
                                    )
                                else:
                                    dados_solicitacao = {
                                        "nome": nome_p,
                                        "contato": contato_p,
                                        "detalhes": detalhe_p,
                                        "data_agendamento": datetime.datetime.now().strftime(
                                            "%d/%m/%Y %H:%M"
                                        ),
                                    }

                                    for obj in st.session_state.banco_objetos:
                                        if obj["codigo"] == item["codigo"]:
                                            obj["status"] = "Agendado"
                                            obj["dados_agendamento"] = dados_solicitacao
                                            break

                                    st.session_state.solicitacoes_resgate.append({
                                        "codigo_item": item["codigo"],
                                        "descricao_item": item["descricao"],
                                        **dados_solicitacao,
                                    })

                                    qr_bytes = gerar_qrcode_bytes(
                                        f"RETIRADA-{item['codigo']}-{nome_p}"
                                    )
                                    st.success(
                                        f"Solicitação enviada com sucesso! O item {item['codigo']}"
                                        " foi marcado como Agendado no painel da Unimar."
                                    )
                                    st.image(
                                        qr_bytes,
                                        caption=(
                                            "Apresente este QR Code no local de retirada"
                                            f" ({item['localizacao']})"
                                        ),
                                        width=200,
                                    )
                                    st.rerun()

    with col_solicitar:
        st.markdown("### 📢 Não encontrou seu pertence?")
        st.caption(
            "Deixe um alerta registrado para que a equipe te avise caso o objeto"
            " seja encontrado no ônibus."
        )

        with st.form(key="form_alerta_perda"):
            item_perdido = st.text_input(
                "O que você perdeu?", placeholder="Ex: Óculos de grau com armação preta"
            )
            linha_onibus = st.text_input("Linha ou horário do ônibus (se souber):")
            data_perda = st.date_input("Data do ocorrido:", datetime.date.today())
            nome_contato = st.text_input("Seu Nome:")
            tel_contato = st.text_input("Seu Telefone / WhatsApp:")

            sub_alerta = st.form_submit_button("🚀 Cadastrar Alerta de Perda")

            if sub_alerta:
                if not item_perdido or not tel_contato:
                    st.error("Preencha ao menos o que foi perdido e o telefone de contato.")
                else:
                    novo_alerta = {
                        "id": f"ALT-{random.randint(1000, 9999)}",
                        "item_perdido": item_perdido,
                        "linha_onibus": linha_onibus if linha_onibus else "Não informada",
                        "data_perda": data_perda.strftime("%d/%m/%Y"),
                        "nome_contato": nome_contato,
                        "tel_contato": tel_contato,
                        "data_registro": datetime.datetime.now().strftime(
                            "%d/%m/%Y %H:%M"
                        ),
                    }
                    st.session_state.alertas_perda.append(novo_alerta)
                    st.success(
                        "Alerta registrado! As informações foram enviadas para o painel"
                        " administrativo da Unimar."
                    )
                    st.rerun()

# =========================================================
# TELA DO ADMINISTRADOR (PROTEGIDA POR LOGIN)
# =========================================================
else:
    render_logo_header()

    if not st.session_state.admin_logado:
        st.warning(
            "🔒 Acesso Restrito: Por favor, insira sua senha de administrador na"
            " barra lateral esquerda para acessar o painel de gestão."
        )
    else:
        st.title("⚙️ Painel de Gestão - Equipe Unimar")
        st.write(
            "Plataforma administrativa de controle de achados e perdidos com"
            " segurança e QR Code."
        )
        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        # 1. ITENS CADASTRADOS E ALERTAS DE PASSAGEIROS
        with col1:
            st.markdown("### 📦 1. Registros e Solicitações")
            st.caption("Visualização, edição, exclusão e alertas de passageiros.")

            aba_selecionada = st.radio(
                "Exibir lista de:",
                ["Aguardando Retirada", "Itens Devolvidos", "📢 Alertas de Perda"],
                key="radio_admin_itens",
            )

            st.markdown("---")

            if aba_selecionada == "Aguardando Retirada":
                pendentes = [
                    i
                    for i in st.session_state.banco_objetos
                    if i["status"] in ["Disponível", "Agendado"]
                ]
                st.write(f"Total pendente: {len(pendentes)}")
                for item in pendentes:
                    tag_status = (
                        "🟡 Agendado para Retirada"
                        if item["status"] == "Agendado"
                        else "🟢 Disponível"
                    )
                    with st.expander(f"📌 {item['codigo']} - {item['descricao']}"):
                        st.write(f"Local: {item['localizacao']}")
                        st.write(f"Status: {tag_status}")

                        if item["status"] == "Agendado" and item.get("dados_agendamento"):
                            st.markdown("---")
                            st.write("👤 Informações do Agendamento pelo Passageiro:")
                            ag = item["dados_agendamento"]
                            st.write(f"• **Nome:** {ag.get('nome')}")
                            st.write(f"• **Contato/WhatsApp:** {ag.get('contato')}")
                            st.write(
                                f"• **Detalhes do Item:** {ag.get('detalhes', 'Não informado')}"
                            )
                            st.write(f"• **Data/Hora Solicitado:** {ag.get('data_agendamento')}")
                            st.markdown("---")

                        if item.get("foto_item"):
                            st.image(
                                item["foto_item"],
                                caption="Foto Registrada",
                                use_container_width=True,
                            )

                        qr_bytes = gerar_qrcode_bytes(f"VALIDAR-{item['codigo']}")
                        st.image(qr_bytes, caption="QR Code do Item", width=150)

                        with st.form(key=f"form_edit_{item['codigo']}"):
                            nova_desc = st.text_input(
                                "Editar Descrição:", value=item["descricao"]
                            )
                            novo_local = st.selectbox(
                                "Editar Local:",
                                ["Vila das Contratadas / Vale", "Garagem Unimar"],
                                index=(
                                    0
                                    if item["localizacao"] == "Vila das Contratadas / Vale"
                                    else 1
                                ),
                            )
                            btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações")

                            if btn_salvar_edicao:
                                item["descricao"] = nova_desc
                                item["localizacao"] = novo_local
                                st.success("Registro atualizado com sucesso!")
                                st.rerun()

                        if st.button("🗑️ Excluir Registro", key=f"del_{item['codigo']}"):
                            st.session_state.banco_objetos = [
                                i
                                for i in st.session_state.banco_objetos
                                if i["codigo"] != item["codigo"]
                            ]
                            st.success(f"Item {item['codigo']} excluído!")
                            st.rerun()

            elif aba_selecionada == "Itens Devolvidos":
                entregues = [
                    i for i in st.session_state.banco_objetos if i["status"] == "Entregue"
                ]
                st.write(f"Total entregue: {len(entregues)}")
                for item in entregues:
                    with st.expander(f"✅ {item['codigo']} - {item['descricao']}"):
                        st.write(f"Local: {item['localizacao']}")
                        if item.get("foto_item"):
                            st.image(
                                item["foto_item"],
                                caption="Foto Registrada",
                                use_container_width=True,
                            )
                        if item["dados_entrega"]:
                            st.write(f"Recebedor: {item['dados_entrega']['nome']}")
                            st.write(f"Data: {item['dados_entrega']['data_hora']}")

            else:
                alertas = st.session_state.alertas_perda
                st.write(f"Total de Alertas Registrados: {len(alertas)}")

                if not alertas:
                    st.info("Nenhum alerta de perda pendente enviado por passageiros.")
                else:
                    for idx, alt in enumerate(alertas):
                        with st.expander(f"⚠️ {alt['id']} — {alt['item_perdido']}"):
                            st.write(f"🚌 Linha/Horário: {alt['linha_onibus']}")
                            st.write(f"📅 Data do Ocorrido: {alt['data_perda']}")
                            st.write(f"👤 Solicitante: {alt['nome_contato']}")
                            st.write(f"📞 Contato/WhatsApp: {alt['tel_contato']}")
                            st.caption(f"Registrado em: {alt['data_registro']}")

                            if st.button(
                                "🗑️ Excluir Alerta do Ficheiro",
                                key=f"del_alt_{alt['id']}_{idx}",
                            ):
                                st.session_state.alertas_perda.pop(idx)
                                st.success("Alerta removido do ficheiro!")
                                st.rerun()

        # 2. CADASTRAR NOVO ITEM
        with col2:
            st.markdown("### ➕ 2. Cadastrar Novo Item")
            st.caption("Registro rápido com código único garantido.")

            desc_novo = st.text_input(
                "Descrição do Objeto Encontrado:",
                placeholder="Ex: Carteira de couro preta",
            )
            linha_nova = st.text_input(
                "Linha/Ônibus onde foi encontrado:", placeholder="Ex: Rota Industrial"
            )

            local_guarda = st.radio(
                "Local de Guarda:",
                ["Vila das Contratadas / Vale", "Garagem Unimar"],
                key="radio_local_admin",
            )

            st.markdown("---")

            if "cam_item_ativa" not in st.session_state:
                st.session_state.cam_item_ativa = False
            if "foto_item_temp" not in st.session_state:
                st.session_state.foto_item_temp = None

            if not st.session_state.cam_item_ativa:
                if st.button(
                    "📷 Abrir Câmera para Fotografar Item", key="btn_abrir_cam_item"
                ):
                    st.session_state.cam_item_ativa = True
                    st.rerun()
            else:
                st.warning(
                    "⚠️ Permissão do Dispositivo: Por favor, permita o acesso à"
                    " câmera."
                )
                captura = st.camera_input("Fotografar Item", key="camera_item_input")

                if captura:
                    st.image(
                        captura,
                        caption="Pré-visualização da Imagem",
                        use_container_width=True,
                    )
                    col_save, col_clear = st.columns(2)

                    with col_save:
                        if st.button(
                            "💾 Salvar Foto", type="primary", key="save_img_item"
                        ):
                            st.session_state.foto_item_temp = captura.getvalue()
                            st.success("Imagem salva com sucesso!")

                    with col_clear:
                        if st.button("🗑️ Limpar Foto", key="clear_img_item"):
                            st.session_state.foto_item_temp = None
                            st.session_state.cam_item_ativa = False
                            st.rerun()

            if st.session_state.foto_item_temp is not None:
                st.info("📷 Foto anexada e pronta para o cadastro.")

            st.markdown("---")

            if st.button(
                "✅ Finalizar Cadastro e Gerar Matrícula",
                type="primary",
                use_container_width=True,
            ):
                if not desc_novo.strip():
                    st.error("Por favor, preencha a descrição do item.")
                else:
                    codigos_existentes = [
                        i["codigo"] for i in st.session_state.banco_objetos
                    ]
                    while True:
                        codigo_gerado = f"UNI-{random.randint(1000, 9999)}"
                        if codigo_gerado not in codigos_existentes:
                            break

                    data_hoje = datetime.datetime.now().strftime("%d/%m/%Y")

                    novo_registro = {
                        "codigo": codigo_gerado,
                        "descricao": desc_novo,
                        "linha": linha_nova if linha_nova else "Frota Geral",
                        "localizacao": local_guarda,
                        "data_registro": data_hoje,
                        "status": "Disponível",
                        "foto_item": st.session_state.foto_item_temp,
                        "dados_agendamento": None,
                        "dados_entrega": None,
                    }

                    st.session_state.banco_objetos.append(novo_registro)
                    st.success(f"Cadastro realizado! Código Único: {codigo_gerado}")

                    st.session_state.cam_item_ativa = False
                    st.session_state.foto_item_temp = None
                    st.rerun()

        # 3. ANÁLISE DE DEVOLUÇÕES & QR CODE
        with col3:
            st.markdown("### 📋 3. Análise de Devoluções")
            st.caption("Validação por QR Code e baixa final de entrega.")

            opcao_devolucao = st.radio(
                "Selecione a Ação:",
                ["Informações do Recebedor", "Fotografar Recebedor/Documento"],
                key="radio_devolucao_admin",
            )

            st.markdown("---")

            if opcao_devolucao == "Informações do Recebedor":
                st.write("Galeria de Comprovantes Registrados:")
                entregues = [
                    i for i in st.session_state.banco_objetos if i["status"] == "Entregue"
                ]

                if not entregues:
                    st.info("Nenhum histórico de recebedor salvo até o momento.")
                else:
                    for item in entregues:
                        dados = item.get("dados_entrega", {})
                        with st.expander(
                            f"👤 {dados.get('nome', 'Sem nome')} ({item['codigo']})"
                        ):
                            st.write(f"Item: {item['descricao']}")
                            st.write(f"Documento: {dados.get('documento', 'N/A')}")
                            st.write(f"Data/Hora: {dados.get('data_hora', 'N/A')}")

                            if dados.get("foto_recebedor"):
                                st.image(
                                    dados["foto_recebedor"],
                                    caption="Comprovante / Rosto do Recebedor",
                                    use_container_width=True,
                                )

            else:
                st.write("Dar Baixa / Registrar Entrega:")
                pendentes = [
                    i
                    for i in st.session_state.banco_objetos
                    if i["status"] in ["Disponível", "Agendado"]
                ]

                if not pendentes:
                    st.info("Nenhum item pendente para entrega no momento.")
                else:
                    item_selecionado = st.selectbox(
                        "Selecione o Item para Entrega:",
                        [f"{i['codigo']} - {i['descricao']}" for i in pendentes],
                    )
                    codigo_item = item_selecionado.split(" - ")[0]

                    item_obj = next(
                        (i for i in pendentes if i["codigo"] == codigo_item), None
                    )

                    nome_preenchido = (
                        item_obj["dados_agendamento"]["nome"]
                        if (item_obj and item_obj.get("dados_agendamento"))
                        else ""
                    )

                    nome_rec = st.text_input(
                        "Nome Completo do Passageiro Recebedor:", value=nome_preenchido
                    )
                    doc_rec = st.text_input("Documento (CPF / RG):")

                    if "cam_dev_ativa" not in st.session_state:
                        st.session_state.cam_dev_ativa = False
                    if "foto_dev_temp" not in st.session_state:
                        st.session_state.foto_dev_temp = None

                    if not st.session_state.cam_dev_ativa:
                        if st.button(
                            "📷 Fotografar Recebedor / Documento", key="btn_abrir_cam_dev"
                        ):
                            st.session_state.cam_dev_ativa = True
                            st.rerun()
                    else:
                        st.warning(
                            "⚠️ Permissão do Dispositivo: Por favor, permita o acesso à"
                            " câmera."
                        )
                        captura_dev = st.camera_input(
                            "Capturar Rosto / Documento", key="camera_dev_input"
                        )

                        if captura_dev:
                            st.image(
                                captura_dev,
                                caption="Foto do Recebedor/Documento",
                                use_container_width=True,
                            )
                            col_save_dev, col_clear_dev = st.columns(2)

                            with col_save_dev:
                                if st.button("💾 Salvar Foto", key="save_img_dev"):
                                    st.session_state.foto_dev_temp = captura_dev.getvalue()
                                    st.success("Foto armazenada!")

                    st.markdown("---")
                    if st.button(
                        "✅ Confirmar Devolução do Item",
                        type="primary",
                        use_container_width=True,
                    ):
                        if not nome_rec or not doc_rec:
                            st.error("Preencha o nome e o documento do recebedor.")
                        elif item_obj:
                            data_hora_atual = datetime.datetime.now().strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            item_obj["status"] = "Entregue"
                            item_obj["dados_entrega"] = {
                                "nome": nome_rec,
                                "documento": doc_rec,
                                "data_hora": data_hora_atual,
                                "foto_recebedor": st.session_state.foto_dev_temp,
                            }
                            st.success(
                                f"Item {codigo_item} marcado como Entregue com sucesso!"
                            )
                            st.session_state.cam_dev_ativa = False
                            st.session_state.foto_dev_temp = None
                            st.rerun()