import base64
import datetime
from io import BytesIO
import json
import os
import random
import qrcode
import streamlit as st

# Arquivo JSON onde os dados ficam salvos permanentemente
ARQUIVO_BANCO = "banco_dados.json"


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


# Carrega os dados atualizados do banco no estado da sessão
dados_globais = carregar_dados()
st.session_state.banco_objetos = dados_globais.get("banco_objetos", [])
st.session_state.alertas_perda = dados_globais.get("alertas_perda", [])


# ---------------------------------------------------------
# CONFIGURAÇÃO VISUAL & ESTILO CSS RESPONSIVO
# ---------------------------------------------------------
def get_base64_of_bin_file(bin_file):
  try:
    with open(bin_file, "rb") as f:
      return base64.b64encode(f.read()).decode()
  except Exception:
    return ""


bin_str = get_base64_of_bin_file("1001217215.jpg")
bg_img_css = f'url("data:image/jpeg;base64,{bin_str}")' if bin_str else "none"

st.set_page_config(
    page_title="Unimar - Achados e Perdidos", page_icon="🚌", layout="wide"
)

st.markdown(
    f"""
    <style>
    .block-container {{ padding: 2rem 3rem; }}
    
    /* Fundo adaptável para qualquer dispositivo (PC, Celular, Tablet) */
    .stApp {{
        background-image: linear-gradient(rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.90)), {bg_img_css};
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
        background-color: #0F172A;
        min-height: 100vh;
    }}

    @media (max-width: 768px) {{
        .stApp {{
            background-size: cover;
            background-position: center top;
        }}
    }}

    html, body, [class*="css"], div, p, span, label {{
        font-family: -apple-system, sans-serif !important; color: #FFFFFF !important;
    }}
    h1, h2, h3, .stApp h1, .stApp h2, .stApp h3 {{ color: #4DA8DA !important; font-weight: 700 !important; }}
    
    /* Textos digitados em AZUL nas caixas de input e select */
    input, textarea, select, div[data-baseweb="select"] span, div[data-baseweb="select"] div {{ 
        color: #1D61B0 !important; 
        background-color: #FFFFFF !important; 
        font-weight: 600 !important;
    }}
    
    div[data-testid="stColumn"] > div {{
        background-color: rgba(30, 41, 59, 0.85); border: 1px solid rgba(77, 168, 218, 0.3);
        border-radius: 14px; padding: 20px; backdrop-filter: blur(10px);
    }}
    .stButton>button {{ background-color: #1D61B0 !important; color: #FFFFFF !important; border-radius: 8px; font-weight: 600; }}
    section[data-testid="stSidebar"] {{ background-color: rgba(15, 23, 42, 0.98) !important; }}
    </style>
""",
    unsafe_allow_html=True,
)


def render_logo_header():
  st.markdown(
      """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #4DA8DA; font-size: 2.5rem; margin: 0;">🚌 UNIMAR</h1>
            <p style="color: #94A3B8; font-size: 1.1rem; letter-spacing: 2px; margin: 0;">SISTEMA DE ACHADOS E PERDIDOS</p>
        </div>
    """,
      unsafe_allow_html=True,
  )


def gerar_qrcode(texto):
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
                st.toast("✅ Agendamento solicitado com sucesso!", icon="🎉")
                st.image(
                    gerar_qrcode(f"RETIRADA-{item['codigo']}-{nome_p}"),
                    caption="Apresente este QR Code no local de retirada",
                    width=180,
                )
                st.rerun()
              else:
                st.error("Preencha nome e telefone de contato.")

  with col_solicitar:
    st.markdown("### 📢 Não encontrou seu pertence?")
    with st.form(key="form_alerta"):
      obj_p = st.text_input("O que você perdeu?")
      linha_p = st.text_input("Linha/Horário do ônibus:")
      data_p = st.date_input("Data do ocorrido:", datetime.date.today())
      nome_c = st.text_input("Seu Nome:")
      tel_c = st.text_input("Seu Telefone/WhatsApp:")

      if st.form_submit_button("🚀 Cadastrar Alerta de Perda"):
        if obj_p and tel_c:
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
          st.toast("✅ Alerta de perda cadastrado!", icon="📢")
          st.rerun()

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
              st.info(
                  f"👤 **Solicitante:** {ag['nome']}\n📞 **Contato:**"
                  f" {ag['contato']}\n📝 **Detalhes:**"
                  f" {ag.get('detalhes', 'N/A')}\n📅 **Data:** {ag.get('data')}"
              )

            if item.get("foto_item"):
              st.image(item["foto_item"], use_container_width=True)

            if st.button("🗑️ Excluir", key=f"del_{item['codigo']}"):
              st.session_state.banco_objetos.remove(item)
              salvar_dados({
                  "banco_objetos": st.session_state.banco_objetos,
                  "alertas_perda": st.session_state.alertas_perda,
              })
              st.toast("Item excluído com sucesso!", icon="🗑️")
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
              st.toast("Registro histórico removido!", icon="🗑️")
              st.rerun()

      else:
        for idx, alt in enumerate(st.session_state.alertas_perda):
          with st.expander(f"⚠️ {alt['id']} - {alt['item']}"):
            st.write(
                f"Contato: {alt['nome']} ({alt['tel']})\nLinha: {alt['linha']}"
            )
            if st.button("🗑️ Remover Alerta", key=f"del_alt_{idx}"):
              st.session_state.alertas_perda.pop(idx)
              salvar_dados({
                  "banco_objetos": st.session_state.banco_objetos,
                  "alertas_perda": st.session_state.alertas_perda,
              })
              st.toast("Alerta removido!", icon="🗑️")
              st.rerun()

    # COLUNA 2: CADASTRAR NOVO ITEM (COM LIMPEZA SEGURA DOS CAMPOS)
    with col2:
      st.markdown("### ➕ 2. Cadastrar Novo Item")
      
      desc_novo = st.text_input(
          "Descrição do Objeto (Obrigatório):",
          key="input_desc_novo"
      )
      linha_nova = st.text_input(
          "Linha/Ônibus onde foi encontrado (Opcional):",
          key="input_linha_nova"
      )
      local_guarda = st.radio(
          "Local de Guarda:", ["Vila das Contratadas / Vale", "Garagem Unimar"]
      )
      
      st.markdown("---")
      st.markdown("📸 **Foto do Objeto**")

      foto_b64 = None
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

      if st.button(
          "✅ Cadastrar Objeto no Sistema",
          type="primary",
          use_container_width=True,
      ):
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
          
          # Salva os dados de forma permanente no arquivo JSON
          salvar_dados({
              "banco_objetos": st.session_state.banco_objetos,
              "alertas_perda": st.session_state.alertas_perda,
          })

          # Limpa os campos através dos widgets do session_state sem causar erro
          st.session_state["input_desc_novo"] = ""
          st.session_state["input_linha_nova"] = ""
          st.session_state.ativar_camera_cadastro = False
          
          # Mensagem temporária que surge e desaparece automaticamente
          st.toast(f"✅ Item {cod_novo} cadastrado com sucesso!", icon="📦")
          st.rerun()
        else:
          st.error("Preencha a descrição do item.")

    # COLUNA 3: ANÁLISE E BAIXA DE DEVOLUÇÕES (COM CÂMERA SOB PERMISSÃO)
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
        st.markdown("📸 **Foto do Recebedor / Documento**")

        foto_recebedor_b64 = None

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
            st.toast(f"✅ Item {cod_sel} baixado e devolvido com sucesso!", icon="🎉")
            st.rerun()
          else:
            st.error("Preencha nome e documento do recebedor.")
      else:
        st.info("Nenhum item pendente para entrega.")