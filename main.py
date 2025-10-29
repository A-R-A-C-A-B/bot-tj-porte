import discord
from discord.ui import Modal, TextInput, View
from discord import app_commands
import os
import re
import asyncio
from datetime import datetime

# CONFIGURAÇÃO DO BOT
intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# MODAL PARA SOLICITAÇÃO DE PORTE
class PorteModal(Modal, title='📋 Solicitação de Porte de Arma - TJ'):
    advogado = TextInput(
        label='Nome Completo do Advogado',
        placeholder='Ex: Dr. Silva OAB/SP-12345',
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )
    
    cliente = TextInput(
        label='Nome Completo do Cliente',
        placeholder='Ex: João Costa',
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )
    
    passaporte = TextInput(
        label='Número do Passaporte',
        placeholder='Ex: 123456789 (apenas números)',
        style=discord.TextStyle.short,
        required=True,
        max_length=11
    )
    
    motivo = TextInput(
        label='Motivo da Solicitação',
        placeholder='Descreva detalhadamente o motivo do porte...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        # VALIDAÇÃO DO PASSAPORTE
        passaporte_limpo = re.sub(r'[\.\-\s]', '', self.passaporte.value)
        
        if not passaporte_limpo.isdigit():
            await interaction.response.send_message(
                '❌ **PASSAPORTE INVÁLIDO!**\nDeve conter apenas números (0-9)',
                ephemeral=True
            )
            return
            
        if len(passaporte_limpo) > 11:
            await interaction.response.send_message(
                '❌ **PASSAPORTE INVÁLIDO!**\nMáximo 11 dígitos permitidos',
                ephemeral=True
            )
            return
        
        # VERIFICA SE JUIZ ESTÁ SOLICITANDO PRÓPRIO PORTE
        cargos_usuario = [role.name for role in interaction.user.roles]
        nome_usuario = interaction.user.display_name
        
        if "Juiz" in cargos_usuario and self.advogado.value == nome_usuario and self.cliente.value == nome_usuario:
            await interaction.response.send_message(
                '❌ **SOLICITAÇÃO BLOQUEADA!**\n'
                'Juízes não podem solicitar **próprio porte** diretamente.\n'
                '📋 **Solução:** Peça a um **advogado** para solicitar seu porte.',
                ephemeral=True
            )
            return
        
        # GERAR PROTOCOLO
        protocolo = f"PORT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # CONFIRMAÇÃO DE RECEBIMENTO
        await interaction.response.send_message(
            f'✅ **SOLICITAÇÃO REGISTRADA COM SUCESSO!**\n\n'
            f'**📋 Protocolo:** `{protocolo}`\n'
            f'**👨‍💼 Advogado:** {self.advogado.value}\n'
            f'**👤 Cliente:** {self.cliente.value}\n'
            f'**🆔 Passaporte:** {self.passaporte.value}\n'
            f'**📝 Motivo:** {self.motivo.value}\n\n'
            f'⏳ **Status:** Em análise pelo Tribunal',
            ephemeral=False
        )

# VIEW PARA DECISÃO DO JUIZ
class DecisaoView(View):
    def __init__(self, protocolo, fundamentacao):
        super().__init__(timeout=120)
        self.protocolo = protocolo
        self.fundamentacao = fundamentacao
    
    @discord.ui.button(label='✅ DEFERIR', style=discord.ButtonStyle.success, emoji='✅')
    async def deferir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar_decisao(interaction, 'DEFERIDO')
    
    @discord.ui.button(label='❌ INDEFERIR', style=discord.ButtonStyle.danger, emoji='❌')
    async def indeferir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar_decisao(interaction, 'INDEFERIDO')
    
    @discord.ui.button(label='⏸️ ADIAR', style=discord.ButtonStyle.secondary, emoji='⏸️')
    async def adiar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f'⏸️ **ANÁLISE ADIADA**\n**Processo:** {self.protocolo}\n'
            f'📋 Retornará para análise posterior.',
            ephemeral=False
        )
        self.stop()
    
    async def registrar_decisao(self, interaction: discord.Interaction, decisao):
        data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        await interaction.response.send_message(
            f'⚖️ **DECISÃO JUDICIAL REGISTRADA**\n\n'
            f'**Processo:** {self.protocolo}\n'
            f'**Decisão:** {decisao}\n'
            f'**Juiz:** {interaction.user.display_name}\n'
            f'**Data e Hora:** {data_hora}\n\n'
            
            f'✅ **DOCUMENTOS VERIFICADOS:**\n'
            f'• Laudo psicológico: ✅ VÁLIDO\n'
            f'• Antecedentes criminais: ✅ CONFERIDO\n' 
            f'• Documentação pessoal: ✅ REGULAR\n\n'
            
            f'📝 **FUNDAMENTAÇÃO:**\n'
            f'_{self.fundamentacao}_\n\n'
            
            f'🔏 **Registro oficial:** TJ-{self.protocolo}-{decisao}',
            ephemeral=False
        )
        self.stop()

# MODAL PARA ANÁLISE DO JUIZ
class AnaliseModal(Modal, title='⚖️ Análise de Processo - TJ'):
    def __init__(self, protocolo):
        super().__init__()
        self.protocolo = protocolo
        
    fundamentacao = TextInput(
        label='Fundamentação da Decisão',
        placeholder='Descreva a análise dos documentos e fundamentação legal...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        mensagem_confirmacao = (
            f'⚖️ **CONFIRMAÇÃO DE ANÁLISE DOCUMENTAL**\n\n'
            f'**Processo:** {self.protocolo}\n'
            f'**Juiz Relator:** {interaction.user.display_name}\n\n'
            
            f'🔍 **VERIFIQUE OS DOCUMENTOS ANEXOS:**\n'
            f'📋 **1. LAUDO PSICOLÓGICO** - Hospital da Cidade\n'
            f'   → Status: [APTIDÃO/INAPTIDÃO] ✅\n'
            f'   → Data do exame: [CONFIRMAR] ✅\n\n'
            
            f'📋 **2. ANTECEDENTES CRIMINAIS** - Polícia Civil\n'  
            f'   → Status: [NADA CONSTA/COM RESTRIÇÕES] ✅\n'
            f'   → Data da emissão: [CONFIRMAR] ✅\n\n'
            
            f'📋 **3. DOCUMENTAÇÃO PESSOAL**\n'
            f'   → Passaporte: [VÁLIDO] ✅\n'
            f'   → Comprovantes: [CONFERIDOS] ✅\n\n'
            
            f'📝 **FUNDAMENTAÇÃO:**\n'
            f'_{self.fundamentacao.value}_\n\n'
            
            f'**Selecione a decisão abaixo:** ⬇️'
        )
        
        view = DecisaoView(self.protocolo, self.fundamentacao.value)
        await interaction.response.send_message(mensagem_confirmacao, view=view, ephemeral=False)

# COMANDOS SLASH
@tree.command(name="solicitar_porte", description="📋 Solicitar porte de arma - Tribunal de Justiça")
async def solicitar_porte(interaction: discord.Interaction):
    if not any(role.name in ['Advogado', 'Juiz', 'Promotor'] for role in interaction.user.roles):
        await interaction.response.send_message(
            '❌ **ACESSO NEGADO!**\nApenas **Advogados, Juízes e Promotores** podem solicitar porte.',
            ephemeral=True
        )
        return
    
    await interaction.response.send_modal(PorteModal())

@tree.command(name="analisar_processo", description="⚖️ Analisar processo de porte - Apenas Juízes")
async def analisar_processo(interaction: discord.Interaction, protocolo: str):
    if not any(role.name == 'Juiz' for role in interaction.user.roles):
        await interaction.response.send_message(
            '❌ **ACESSO RESTRITO!**\nApenas **Juízes** podem analisar processos.',
            ephemeral=True
        )
        return
    
    await interaction.response.send_modal(AnaliseModal(protocolo))

@tree.command(name="minhas_permissoes", description="🔐 Verificar minhas permissões no sistema")
async def minhas_permissoes(interaction: discord.Interaction):
    cargos_usuario = [role.name for role in interaction.user.roles]
    cargos_permitidos = ['Advogado', 'Juiz', 'Promotor', 'Servidor TJ']
    
    permissoes = []
    for cargo in cargos_usuario:
        if cargo in cargos_permitidos:
            permissoes.append(cargo)
    
    if permissoes:
        await interaction.response.send_message(
            f'✅ **SUAS PERMISSÕES:**\n' + '\n'.join(f'• {p}' for p in permissoes),
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            '❌ **VOCÊ NÃO TEM PERMISSÕES**\n'
            'Cargos permitidos: Advogado, Juiz, Promotor, Servidor TJ',
            ephemeral=True
        )

# EVENTOS DO BOT
@bot.event
async def on_ready():
    await tree.sync()
    print(f'✅ Bot {bot.user.name} está ONLINE!')
    print('🎯 Sistema TJ-Porte carregado com sucesso!')
    print('⚖️ Comandos slash disponíveis!')

# INICIALIZAÇÃO
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print('❌ Token não encontrado! Configure a variável DISCORD_TOKEN')
