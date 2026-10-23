import base64
import datetime
from io import BytesIO
import json
import os
import random

import streamlit as st

# Biblioteca de QR Code (opcional: se não estiver instalada o app continua)
try:
  import qrcode
except ImportError:
  qrcode = None

# Pasta onde o app.py está - garante caminhos estáveis em qualquer máquina
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Arquivo JSON onde os dados ficam salvos permanentemente
ARQUIVO_BANCO = os.path.join(BASE_DIR, "banco_dados.json")


# ---------------------------------------------------------
# FUNÇÕES DE PERSISTÊNCIA DE DADOS (BANCO LOCAL JSON)
# ---------------------------------------------------------
def carregar_dados():
  """Lê os dados salvos no arquivo JSON ou cria o banco inicial se não existir."""
  if not os.path.exists(ARQUIVO_BANCO):
    dados_iniciais = {
        "banco_objetos": [
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
        ],
        "alertas_perda": [],
    }
    salvar_dados(dados_iniciais)
    return dados_iniciais

  try:
    with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    return {"banco_objetos": [], "alertas_perda": []}


def salvar_dados(dados):
  """Escreve as alterações diretamente no arquivo físico para persistência permanente."""
  with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)


# CONFIGURAÇÃO DA PÁGINA (precisa ser o 1º comando Streamlit)
st.set_page_config(
    page_title="Unimar - Achados e Perdidos", page_icon="🚌", layout="wide"
)

# Carrega os dados atualizados do banco no estado da sessão
dados_globais = carregar_dados()
st.session_state.banco_objetos = dados_globais.get("banco_objetos", [])
st.session_state.alertas_perda = dados_globais.get("alertas_perda", [])


# ---------------------------------------------------------
# CONFIGURAÇÃO VISUAL & ESTILO CSS RESPONSIVO
# ---------------------------------------------------------
def notificar(mensagem, icon="✅"):
  """Guarda um aviso que será exibido como toast na próxima execução.

  O st.toast() é descartado quando chamamos st.rerun() logo em seguida,
  por isso a mensagem fica guardada no session_state e é exibida no topo
  do script, antes de qualquer outra coisa ser desenhada.
  """
  st.session_state.flash = {"msg": mensagem, "icon": icon}


def get_base64_of_bin_file(bin_file):
  try:
    with open(bin_file, "rb") as f:
      return base64.b64encode(f.read()).decode()
  except Exception:
    return ""


def achar_imagem_de_fundo():
  """Procura a imagem de fundo do projeto (arquivo opcional)."""
  nomes = ("1001217215.jpg", "fundo.jpg", "background.jpg")
  for pasta in (BASE_DIR, os.getcwd()):
    for nome in nomes:
      caminho = os.path.join(pasta, nome)
      if os.path.exists(caminho):
        return caminho
  return None


caminho_fundo = achar_imagem_de_fundo()
bin_str = get_base64_of_bin_file(caminho_fundo) if caminho_fundo else ""
bg_img_css = f'url("data:image/jpeg;base64,{bin_str}")' if bin_str else "none"

# Exibe avisos pendentes (toasts) antes de desenhar a tela
_flash = st.session_state["flash"] if "flash" in st.session_state else None
if _flash:
  st.toast(_flash["msg"], icon=_flash.get("icon", "✅"))
  st.session_state.flash = None

st.markdown(
    f"""
    <style>
    /* ============ BASE / TIPOGRAFIA ============ */
    /* A fonte é aplicada somente nos "pais" (html/body/.stApp) para não
       quebrar os ícones nativos do Streamlit (Material Icons). */
    html, body, #root, .stApp {{
        font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
    }}

    .block-container {{ padding: 2rem 3rem; }}
    
    /* Fundo adaptável para qualquer dispositivo */
    .stApp {{
        background-image: linear-gradient(rgba(15, 23, 42, 0.84), rgba(15, 23, 42, 0.92)), {bg_img_css};
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
        background-color: #0F172A;
        min-height: 100vh;
    }}

    /* ============ RESPONSIVO ============ */
    @media (max-width: 1100px) {{
        .block-container {{ padding: 1.5rem 1.5rem !important; }}
        div[data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; }}
        div[data-testid="stColumn"] {{ width: 100% !important; flex: 1 1 100% !important; }}
    }}

    @media (max-width: 768px) {{
        .stApp {{
            background-size: cover;
            background-position: center top;
            background-attachment: scroll !important;
        }}
        .block-container {{ padding: 1rem 0.75rem !important; }}
        div[data-testid="stColumn"] > div {{ padding: 14px !important; border-radius: 12px !important; }}
        .stButton>button, div[data-testid="stFormSubmitButton"]>button {{ min-height: 44px; }}
        h1, .stApp h1 {{ font-size: clamp(1.5rem, 6vw, 2.2rem) !important; }}
        h2, h3, .stApp h2, .stApp h3 {{ font-size: clamp(1.15rem, 4.6vw, 1.5rem) !important; }}
    }}

    @media (max-width: 480px) {{
        .block-container {{ padding: 0.75rem 0.5rem !important; }}
        div[data-testid="stColumn"] > div {{ padding: 12px !important; }}
        [data-testid="stDateInputCalendar"] {{ max-width: calc(100vw - 12px) !important; }}
    }}

    /* Texto branco padrão (superfícies claras são reestilizadas abaixo) */
    div, p, span, label, a, li {{ color: #FFFFFF !important; }}
    h1, h2, h3, h4, .stApp h1, .stApp h2, .stApp h3 {{ color: #4DA8DA !important; font-weight: 700 !important; }}

    /* Cabeçalho do logotipo (tamanhos responsivos) */
    .unimar-header {{ text-align: center; margin-bottom: 18px; }}
    .unimar-title {{ color: #4DA8DA !important; font-size: clamp(1.7rem, 5vw, 2.5rem) !important; margin: 0; }}
    .unimar-sub {{ color: #94A3B8 !important; font-size: clamp(0.8rem, 2.6vw, 1.1rem) !important; letter-spacing: 2px; margin: 0; }}
    
    /* Textos digitados em AZUL nas caixas de entrada e selects */
    /* Caixas de entrada brancas com texto azul (design Unimar) */
    input, textarea, select, div[data-baseweb="select"] span, div[data-baseweb="select"] div,
    div[data-testid="stDateInputField"], div[data-testid="stDateInputField"] * {{
        color: #1D61B0 !important;
        background-color: #FFFFFF !important;
        font-weight: 600 !important;
    }}
    
    /* Correção do File Uploader (Caixa de Upload de fotos) */
    div[data-testid="stFileUploader"] {{
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }}
    div[data-testid="stFileUploader"] *, 
    div[data-testid="stFileUploader"] button, 
    div[data-testid="stFileUploader"] span, 
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploaderDropzone"] * {{
        color: #1D61B0 !important;
        font-weight: 700 !important;
    }}
    
    /* ============ CALENDÁRIO (Streamlit 1.44+ / Base UI) ============ */
    /* No Streamlit atual o pop-up usa data-testid="stDateInputCalendar";
       os seletores antigos (data-baseweb="calendar") não existem mais. */
    [data-testid="stDateInputCalendar"],
    [data-testid="stDateInputCalendar"] *,
    [data-testid="stDateTimeInputCalendar"],
    [data-testid="stDateTimeInputCalendar"] * {{
        color: #0F172A !important;
    }}

    [data-testid="stDateInputCalendar"],
    [data-testid="stDateTimeInputCalendar"] {{
        background-color: #FFFFFF !important;
        border: 1px solid rgba(77, 168, 218, 0.45) !important;
        border-radius: 14px !important;
        padding: 10px !important;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.45) !important;
        z-index: 999999 !important;
    }}

    #stFloatingOverlayPortal {{ z-index: 999999 !important; }}

    [data-testid="stDateInputCalendar"] button,
    [data-testid="stDateInputCalendar"] [role="button"],
    [data-testid="stDateInputCalendar"] td,
    [data-testid="stDateInputCalendar"] th {{
        background-color: transparent !important;
        border-radius: 8px !important;
        color: #0F172A !important;
        font-weight: 600 !important;
    }}

    [data-testid="stDateInputCalendar"] button:hover,
    [data-testid="stDateInputCalendar"] [role="button"]:hover {{
        background-color: #DCEBFA !important;
    }}

    [data-testid="stDateInputCalendar"] [data-outside-month="true"] {{
        color: #9AA6B2 !important;
    }}

    [data-testid="stDateInputCalendar"] [data-today="true"] {{
        color: #1D61B0 !important;
        box-shadow: inset 0 0 0 2px #1D61B0 !important;
    }}

    /* Dia selecionado (por último: vence as regras acima) */
    [data-testid="stDateInputCalendar"] [data-selected="true"],
    [data-testid="stDateInputCalendar"] [aria-selected="true"] > [role="button"] {{
        background-color: #1D61B0 !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }}

    /* Listas suspensas (selectbox e mês/ano do calendário) */
    div[role="listbox"],
    div[role="listbox"] * {{
        color: #0F172A !important;
    }}

    div[role="listbox"] {{
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }}

    div[role="option"]:hover {{
        background-color: #DCEBFA !important;
    }}

    div[role="option"][aria-selected="true"] {{
        background-color: #1D61B0 !important;
        color: #FFFFFF !important;
    }}

    /* Estilização dos Botões principais */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{
        background-color: #1D61B0 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        border: 1px solid #4DA8DA !important;
    }}

    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {{
        background-color: #2E7CC4 !important;
        border-color: #7FC4E8 !important;
    }}
    
    div[data-testid="stColumn"] > div {{
        background-color: rgba(30, 41, 59, 0.85); border: 1px solid rgba(77, 168, 218, 0.3);
        border-radius: 14px; padding: 20px; backdrop-filter: blur(10px);
    }}
    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.98) !important;
        border-right: 1px solid rgba(77, 168, 218, 0.25) !important;
    }}
    </style>
""",
    unsafe_allow_html=True,
)


def render_logo_header():
  st.markdown(
      """
        <div class="unimar-header">
            <h1 class="unimar-title">🚌 UNIMAR</h1>
            <p class="unimar-sub">SISTEMA DE ACHADOS E PERDIDOS</p>
        </div>
    """,
      unsafe_allow_html=True,
  )


def gerar_qrcode(texto):
  """Gera a imagem do QR Code (retorna None se a lib qrcode faltar)."""
  if qrcode is None:
    return None
  qr = qrcode.QRCode(version=1, box_size=10, border=2)
  qr.add_data(texto)
  qr.make(fit=True)
  img = qr.make_image(fill_color="black", back_color="white")
  buf = BytesIO()
  img.save(buf, format="PNG")
  return buf.getvalue()


# ---------------------------------------------------------
# NAVEGAÇÃO LATERAL E SEGURANÇA
# ---------------------------------------------------------
if "admin_logado" not in st.session_state:
  st.session_state.admin_logado = False

# Inicialização dos estados de permissão da câmera
if "ativar_camera_cadastro" not in st.session_state:
  st.session_state.ativar_camera_cadastro = False
if "ativar_camera_baixa" not in st.session_state:
  st.session_state.ativar_camera_baixa = False

st.sidebar.markdown("### 🚌 Unimar Transportes")
perfil_acesso = st.sidebar.radio(
    "Modo de Visualização:", ["📱 Tela do Passageiro", "⚙️ Painel do Administrador"]
)

if perfil_acesso == "⚙️ Painel do Administrador":
  if not st.session_state.admin_logado:
    st.sidebar.markdown("---")
    senha = st.sidebar.text_input("Senha do Administrador:", type="password")
    if st.sidebar.button("Entrar no Painel"):
      if senha == "unimar2026":
        st.session_state.admin_logado = True
        st.session_state.ativar_camera_cadastro = False
        st.session_state.ativar_camera_baixa = False
        st.rerun()
      else:
        st.sidebar.error("Senha incorreta!")
  else:
    if st.sidebar.button("🚪 Sair do Painel"):
      st.session_state.admin_logado = False
      st.session_state.ativar_camera_cadastro = False
      st.session_state.ativar_camera_baixa = False
      st.rerun()

# =========================================================
# TELA DO PASSAGEIRO
# =========================================================
if perfil_acesso == "📱 Tela do Passageiro":
  render_logo_header()
  st.write(
      "Esqueceu algum pertence nos veículos da frota? Pesquise abaixo ou"
      " cadastre uma solicitação."
  )
  col_busca, col_solicitar = st.columns([2, 1])

  with col_busca:
    st.markdown("### 🔎 Buscar Item Encontrado")
    termo = st.text_input(
        "Digite o objeto, linha do ônibus ou código:",
        placeholder="Ex: Mochila, Celular, UNI-8492...",
    )

    itens_visiveis = [
        i
        for i in st.session_state.banco_objetos
        if i["status"] in ["Disponível", "Agendado"]
    ]

    if termo:
      itens_visiveis = [
          i
          for i in itens_visiveis
          if termo.lower() in i["descricao"].lower()
          or termo.lower() in i.get("linha", "").lower()
          or termo.lower() in i["codigo"].lower()
      ]

    st.markdown(f"*Itens Encontrados e Guardados ({len(itens_visiveis)}):*")

    for item in itens_visiveis:
      label_item = f"📌 {item['codigo']} — {item['descricao']}"
      if item["status"] == "Agendado":
        label_item += " (🟡 Agendado)"

      with st.expander(label_item):
        st.write(f"🚌 **Linha:** {item.get('linha', 'Geral')}")
        st.write(f"📍 **Local de Retirada:** {item['localizacao']}")
        st.write(f"📅 **Data de Entrada:** {item['data_registro']}")

        if item.get("foto_item"):
          st.image(
              item["foto_item"],
              caption="Foto do Objeto",
              use_container_width=True,
          )

        if item["status"] == "Agendado":
          st.warning("🟡 Este item já possui um agendamento de retirada.")
          if item.get("dados_agendamento"):
            st.write(f"👤 **Solicitante:** {item['dados_agendamento']['nome']}")

          # QR Code gerado nesta solicitação (sobrevive ao st.rerun)
          qr_info = st.session_state.get("qr_exibicao")
          if qr_info and qr_info.get("codigo") == item["codigo"]:
            if qr_info.get("img"):
              st.image(
                  qr_info["img"],
                  caption="Apresente este QR Code no local de retirada",
                  width=180,
              )
            else:
              st.code(qr_info.get("texto", ""), language="text")
            if st.button(
                "✖️ Fechar QR Code", key=f"fechar_qr_{item['codigo']}"
            ):
              st.session_state.qr_exibicao = None
              st.rerun()
        else:
          with st.form(key=f"form_{item['codigo']}"):
            nome_p = st.text_input("Seu Nome Completo:")
            contato_p = st.text_input("Telefone/WhatsApp:")
            detalhe_p = st.text_area("Detalhes do pertence para confirmação:")

            if st.form_submit_button("📩 Solicitar Retirada"):
              if nome_p and contato_p:
                item["status"] = "Agendado"
                item["dados_agendamento"] = {
                    "nome": nome_p,
                    "contato": contato_p,
                    "detalhes": detalhe_p,
                    "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
                salvar_dados({
                    "banco_objetos": st.session_state.banco_objetos,
                    "alertas_perda": st.session_state.alertas_perda,
                })
                # Guarda o QR Code para exibir depois do recarregamento
                codigo_qr = f"RETIRADA-{item['codigo']}-{nome_p}"
                st.session_state.qr_exibicao = {
                    "codigo": item["codigo"],
                    "texto": codigo_qr,
                    "img": gerar_qrcode(codigo_qr),
                }
                notificar("✅ Agendamento solicitado com sucesso!", "🎉")
                st.rerun()
              else:
                st.error("Preencha nome e telefone de contato.")

  with col_solicitar:
    st.markdown("### 📢 Não encontrou seu pertence?")
    with st.form(key="form_alerta_perda", clear_on_submit=True):
      obj_p = st.text_input("O que você perdeu?")
      linha_p = st.text_input("Linha/Horário do ônibus:")
      data_p = st.date_input("Data do ocorrido:", datetime.date.today())
      nome_c = st.text_input("Seu Nome:")
      tel_c = st.text_input("Seu Telefone/WhatsApp:")

      btn_alerta = st.form_submit_button("🚀 Cadastrar Alerta de Perda", use_container_width=True)

      if btn_alerta:
        if obj_p.strip() and tel_c.strip():
          st.session_state.alertas_perda.append({
              "id": f"ALT-{random.randint(1000, 9999)}",
              "item": obj_p,
              "linha": linha_p or "Não informada",
              "data": data_p.strftime("%d/%m/%Y"),
              "nome": nome_c,
              "tel": tel_c,
          })
          salvar_dados({
              "banco_objetos": st.session_state.banco_objetos,
              "alertas_perda": st.session_state.alertas_perda,
          })
          notificar(
              "✅ Alerta registrado com sucesso e enviado ao Administrador!",
              "📢",
          )
          st.rerun()
        else:
          st.error("Preencha o que perdeu e o telefone de contato.")

# =========================================================
# TELA DO ADMINISTRADOR (VISÃO RESTRITA)
# =========================================================
else:
  render_logo_header()

  if not st.session_state.admin_logado:
    st.warning(
        "🔒 **Acesso Restrito:** Digite a senha na barra lateral para acessar o"
        " painel."
    )
  else:
    st.title("⚙️ Painel de Gestão - Equipe Unimar")
    col1, col2, col3 = st.columns(3)

    # COLUNA 1: CONSULTA DE REGISTROS
    with col1:
      st.markdown("### 📦 1. Registros e Solicitações")
      aba = st.radio(
          "Exibir:", ["Aguardando Retirada", "Itens Devolvidos", "Alertas"]
      )

      if aba == "Aguardando Retirada":
        pendentes = [
            i
            for i in st.session_state.banco_objetos
            if i["status"] in ["Disponível", "Agendado"]
        ]
        st.write(f"**Total:** {len(pendentes)}")

        for item in pendentes:
          label_item = f"📌 {item['codigo']} - {item['descricao']}"
          with st.expander(label_item):
            st.write(f"📍 **Local:** {item['localizacao']}")
            st.write(f"🚌 **Linha:** {item.get('linha', 'Geral')}")
            st.write(f"📊 **Status:** {item['status']}")

            if item.get("dados_agendamento"):
              ag = item["dados_agendamento"]
              st.info(f"👤 **Solicitante:** {ag['nome']}")
              st.write(f"📞 **Contato:** {ag.get('contato', 'N/A')}")
              st.write(f"📝 **Detalhes:** {ag.get('detalhes', 'N/A')}")
              st.write(f"📅 **Data:** {ag.get('data', 'N/A')}")

            if item.get("foto_item"):
              st.image(item["foto_item"], use_container_width=True)

            if st.button("🗑️ Excluir", key=f"del_{item['codigo']}"):
              st.session_state.banco_objetos.remove(item)
              salvar_dados({
                  "banco_objetos": st.session_state.banco_objetos,
                  "alertas_perda": st.session_state.alertas_perda,
              })
              notificar("Item excluído com sucesso!", "🗑️")
              st.rerun()

      elif aba == "Itens Devolvidos":
        entregues = [
            i for i in st.session_state.banco_objetos if i["status"] == "Entregue"
        ]
        for item in entregues:
          with st.expander(f"✅ {item['codigo']} - {item['descricao']}"):
            ent = item.get("dados_entrega", {})
            st.write(f"👤 **Recebedor:** {ent.get('nome', 'N/A')}")
            st.write(f"🪪 **Documento:** {ent.get('documento', 'N/A')}")
            st.write(f"📅 **Data/Hora:** {ent.get('data', 'N/A')}")
            if ent.get("foto_recebedor"):
              st.image(
                  ent["foto_recebedor"],
                  caption="Foto do Recebedor / Documento",
                  use_container_width=True,
              )
            if st.button("🗑️ Excluir Histórico", key=f"del_ent_{item['codigo']}"):
              st.session_state.banco_objetos.remove(item)
              salvar_dados({
                  "banco_objetos": st.session_state.banco_objetos,
                  "alertas_perda": st.session_state.alertas_perda,
              })
              notificar("Registro histórico removido!", "🗑️")
              st.rerun()

      else:
        st.write(f"**Total de Alertas:** {len(st.session_state.alertas_perda)}")
        for idx, alt in enumerate(st.session_state.alertas_perda):
          with st.expander(f"⚠️ {alt['id']} - {alt['item']}"):
            st.write(f"👤 **Contato:** {alt['nome']} ({alt['tel']})")
            st.write(f"🚌 **Linha/Horário:** {alt['linha']}")
            st.write(f"📅 **Data da Perda:** {alt['data']}")
            if st.button("🗑️ Remover Alerta", key=f"del_alt_{idx}"):
              st.session_state.alertas_perda.pop(idx)
              salvar_dados({
                  "banco_objetos": st.session_state.banco_objetos,
                  "alertas_perda": st.session_state.alertas_perda,
              })
              notificar("Alerta removido!", "🗑️")
              st.rerun()

    # COLUNA 2: CADASTRAR NOVO ITEM (COM OPÇÃO DE CÂMERA OU UPLOAD)
    with col2:
      st.markdown("### ➕ 2. Cadastrar Novo Item")
      
      with st.form(key="form_cadastro_item", clear_on_submit=True):
        desc_novo = st.text_input("Descrição do Objeto (Obrigatório):")
        linha_nova = st.text_input("Linha/Ônibus onde foi encontrado (Opcional):")
        local_guarda = st.radio(
            "Local de Guarda:", ["Vila das Contratadas / Vale", "Garagem Unimar"]
        )
        
        btn_cadastrar = st.form_submit_button("✅ Cadastrar Objeto no Sistema", use_container_width=True)

      st.markdown("---")
      st.markdown("📸 **Foto do Objeto (Câmera ou Upload)**")

      foto_b64 = None
      
      # Opção de Upload de arquivo do dispositivo
      arquivo_upload = st.file_uploader("Enviar imagem do dispositivo", type=["jpg", "jpeg", "png"], key="upload_cad")
      if arquivo_upload:
        foto_b64 = f"data:image/jpeg;base64,{base64.b64encode(arquivo_upload.getvalue()).decode()}"
        st.image(arquivo_upload, caption="Pré-visualização do Upload", width=200)

      if not st.session_state.ativar_camera_cadastro:
        if st.button("🔓 Ativar Câmera para Fotografar Objeto"):
          st.session_state.ativar_camera_cadastro = True
          st.rerun()
      else:
        st.info("Permissão concedida. Câmera pronta para uso.")
        foto_captura = st.camera_input("Fotografar Item")
        if foto_captura:
          foto_b64 = f"data:image/jpeg;base64,{base64.b64encode(foto_captura.getvalue()).decode()}"
        
        if st.button("🔒 Desativar Câmera de Cadastro"):
          st.session_state.ativar_camera_cadastro = False
          st.rerun()

      st.markdown("---")

      if btn_cadastrar:
        if desc_novo.strip():
          cod_novo = f"UNI-{random.randint(1000, 9999)}"
          novo_item = {
              "codigo": cod_novo,
              "descricao": desc_novo,
              "linha": linha_nova or "Frota Geral",
              "localizacao": local_guarda,
              "data_registro": datetime.datetime.now().strftime("%d/%m/%Y"),
              "status": "Disponível",
              "foto_item": foto_b64,
              "dados_agendamento": None,
              "dados_entrega": None,
          }
          st.session_state.banco_objetos.append(novo_item)
          
          # Salva permanentemente no JSON
          salvar_dados({
              "banco_objetos": st.session_state.banco_objetos,
              "alertas_perda": st.session_state.alertas_perda,
          })

          st.session_state.ativar_camera_cadastro = False
          
          # Exibe notificação temporária e atualiza a tela limpando tudo
          notificar(f"✅ Item {cod_novo} cadastrado com sucesso!", "📦")
          st.rerun()
        else:
          st.error("Preencha a descrição do item.")
# COLUNA 3: ANÁLISE E BAIXA DE DEVOLUÇÕES (COM CÂMERA OU UPLOAD)
    with col3:
      st.markdown("### 📋 3. Análise de Devoluções")
      pendentes = [
          i
          for i in st.session_state.banco_objetos
          if i["status"] in ["Disponível", "Agendado"]
      ]

      if pendentes:
        item_sel = st.selectbox(
            "Selecione o Item para Baixa:",
            [f"{i['codigo']} - {i['descricao']}" for i in pendentes],
        )
        cod_sel = item_sel.split(" - ")[0]
        obj_sel = next(i for i in pendentes if i["codigo"] == cod_sel)

        nome_preen = (
            obj_sel["dados_agendamento"]["nome"]
            if obj_sel.get("dados_agendamento")
            else ""
        )
        nome_rec = st.text_input("Nome do Recebedor:", value=nome_preen)
        doc_rec = st.text_input("Documento (CPF/RG):")

        st.markdown("---")
        st.markdown("📸 **Foto do Recebedor / Documento (Câmera ou Upload)**")

        foto_recebedor_b64 = None

        # Opção de Upload para o recebedor/documento
        arquivo_upload_rec = st.file_uploader("Enviar documento/foto do dispositivo", type=["jpg", "jpeg", "png"], key="upload_baixa")
        if arquivo_upload_rec:
          foto_recebedor_b64 = f"data:image/jpeg;base64,{base64.b64encode(arquivo_upload_rec.getvalue()).decode()}"
          st.image(arquivo_upload_rec, caption="Pré-visualização do Documento/Recebedor", width=200)

        if not st.session_state.ativar_camera_baixa:
          if st.button("🔓 Ativar Câmera para Documento/Recebedor"):
            st.session_state.ativar_camera_baixa = True
            st.rerun()
        else:
          st.info("Permissão concedida. Câmera pronta para uso.")
          foto_rec = st.camera_input("Fotografar Recebedor ou Documento")
          if foto_rec:
            foto_recebedor_b64 = f"data:image/jpeg;base64,{base64.b64encode(foto_rec.getvalue()).decode()}"
          
          if st.button("🔒 Desativar Câmera de Baixa"):
            st.session_state.ativar_camera_baixa = False
            st.rerun()

        st.markdown("---")

        if st.button(
            "✅ Confirmar Entrega do Item",
            type="primary",
            use_container_width=True,
        ):
          if nome_rec and doc_rec:
            obj_sel["status"] = "Entregue"
            obj_sel["dados_entrega"] = {
                "nome": nome_rec,
                "documento": doc_rec,
                "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "foto_recebedor": foto_recebedor_b64,
            }
            st.session_state.ativar_camera_baixa = False
            salvar_dados({
                "banco_objetos": st.session_state.banco_objetos,
                "alertas_perda": st.session_state.alertas_perda,
            })
            notificar(f"✅ Item {cod_sel} baixado e devolvido com sucesso!", "🎉")
            st.rerun()
          else:
            st.error("Preencha nome e documento do recebedor.")
      else:
        st.info("Nenhum item pendente para entrega.")