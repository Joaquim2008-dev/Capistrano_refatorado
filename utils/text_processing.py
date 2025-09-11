from unidecode import unidecode
import pandas as pd

def padronizar_reu(reu_text):
    """
    Padroniza nomes de réus, especialmente bancos e instituições
    """
    if pd.isna(reu_text) or str(reu_text).strip() == '':
        return 'NÃO INFORMADO'
    
    # Normalizar: maiúsculo e sem acentos
    texto = unidecode(str(reu_text).upper().strip())
    
    # INSS - qualquer texto que contenha INSS
    if 'INSS' in texto:
        return 'INSS'
    
    # CAIXA ECONÔMICA FEDERAL - diversas variações
    if any(palavra in texto for palavra in ['CAIXA ECONOMICA', 'CEF', 'CAIXA FEDERAL']):
        return 'CAIXA'
    elif 'CAIXA' in texto and ('BANCO' in texto or 'FEDERAL' in texto or len(texto.split()) == 1):
        return 'CAIXA'
    
    # BANCO DO BRASIL
    if any(variacao in texto for variacao in ['BANCO DO BRASIL', 'BANCO BRASIL']):
        return 'BANCO DO BRASIL'
    elif texto in ['BB', 'B.B.'] or (len(texto) <= 5 and 'BB' in texto):
        return 'BANCO DO BRASIL'
    
    # BRADESCO
    if 'BRADESCO' in texto:
        return 'BRADESCO'
    
    # ITAÚ
    if any(variacao in texto for variacao in ['ITAU', 'ITAÚ', 'BANCO ITAU']):
        return 'ITAU'
    
    # SANTANDER
    if 'SANTANDER' in texto:
        return 'SANTANDER'
    
    # CREFISA
    if 'CREFISA' in texto:
        return 'CREFISA'
    
    # BMG
    if 'BMG' in texto or 'BANCO BMG' in texto:
        return 'BMG'
    
    # PAN
    if 'BANCO PAN' in texto or (len(texto) <= 10 and 'PAN' in texto):
        return 'BANCO PAN'
    
    # INTER
    if 'BANCO INTER' in texto or 'INTER' in texto:
        return 'BANCO INTER'
    
    # SAFRA
    if 'SAFRA' in texto:
        return 'BANCO SAFRA'
    
    # ORIGINAL
    if 'ORIGINAL' in texto:
        return 'BANCO ORIGINAL'
    
    # C6 BANK
    if 'C6' in texto or 'C6 BANK' in texto:
        return 'C6 BANK'
    
    # NUBANK
    if 'NUBANK' in texto or 'NU BANK' in texto:
        return 'NUBANK'
    
    # VOTORANTIM
    if 'VOTORANTIM' in texto:
        return 'BANCO VOTORANTIM'
    
    # BV (antigo Votorantim)
    if texto == 'BV' or 'BANCO BV' in texto:
        return 'BANCO BV'
    
    # BANRISUL
    if 'BANRISUL' in texto:
        return 'BANRISUL'
    
    # SICOOB
    if 'SICOOB' in texto:
        return 'SICOOB'
    
    # SICREDI
    if 'SICREDI' in texto:
        return 'SICREDI'
    
    # MERCADO PAGO/MERCADO LIVRE
    if 'MERCADO PAGO' in texto or 'MERCADOPAGO' in texto:
        return 'MERCADO PAGO'
    elif 'MERCADO LIVRE' in texto or 'MERCADOLIVRE' in texto:
        return 'MERCADO LIVRE'
    
    # LOSANGO
    if 'LOSANGO' in texto:
        return 'LOSANGO'
    
    # AYMORÉ
    if 'AYMO' in texto or 'AYMORE' in texto:
        return 'AYMORE'
    
    # BANCO CETELEM
    if 'CETELEM' in texto:
        return 'CETELEM'
    
    # EMPRÉSTIMOS/FINANCEIRAS comuns
    if 'CREDITAS' in texto:
        return 'CREDITAS'
    elif 'OLE' in texto and 'CONSIG' in texto:
        return 'OLE CONSIGNADO'
    elif 'CREDSYSTEM' in texto:
        return 'CREDSYSTEM'
    
    # Se não encontrou padrão específico, retorna o texto limpo
    return texto

def padronizar_competencia(competencia_text):
    """
    Padroniza nomes de competência (foros/comarcas)
    """
    if pd.isna(competencia_text) or str(competencia_text).strip() == '':
        return 'NÃO INFORMADO'
    
    # Normalizar: maiúsculo e sem acentos
    texto = unidecode(str(competencia_text).upper().strip())
    
    # Remover '/SE' do final
    if texto.endswith('/SE'):
        texto = texto[:-3].strip()
    
    # Remover '- SE' do final
    if texto.endswith('- SE'):
        texto = texto[:-4].strip()
    
    # Padrões específicos para Aracaju
    if texto in ['ARACAJU', 'AJU'] or 'ARACAJU' in texto:
        return 'ARACAJU'
    
    # Padrões para Nossa Senhora do Socorro
    socorro_variacoes = ['NOSSA SENHORA DO SOCORRO', 'N. SRA. DO SOCORRO','N.S. DO SOCORRO', 'NS DO SOCORRO', 'SOCORRO']
    if any(variacao in texto for variacao in socorro_variacoes) or texto == 'SOCORRO':
        return 'NOSSA SENHORA DO SOCORRO'
    
    # Padrões para São Cristóvão
    cristovao_variacoes = ['SAO CRISTOVAO', 'S. CRISTOVAO', 'CRISTOVAO']
    if any(variacao in texto for variacao in cristovao_variacoes):
        return 'SAO CRISTOVAO'
    
    # Padrões para Lagarto
    if 'LAGARTO' in texto:
        return 'LAGARTO'
    
    # Padrões para Estância
    if 'ESTANCIA' in texto:
        return 'ESTANCIA'
    
    # Padrões para Itabaiana
    if 'ITABAIANA' in texto and 'INHA' not in texto:
        return 'ITABAIANA'
    
    # Padrões para Propriá
    if 'PROPRIA' in texto:
        return 'PROPRIA'
    
    # Padrões para Tobias Barreto
    if 'TOBIAS' in texto:
        return 'TOBIAS BARRETO'
    
    # Padrões para Barra dos Coqueiros
    if 'BARRA' in texto and 'COQU' in texto:
        return 'BARRA DOS COQUEIROS'
    
    # Se não encontrou padrão específico, retorna o texto limpo
    return texto

def corrigir_municipios(nome):
    """
    Corrige o nome dos municípios com base em regras específicas.
    """
    if pd.isna(nome):
        return ''  # Retorna vazio se for NaN
    
    nome_lower = unidecode(str(nome).lower())
    
    if 'socorro' in nome_lower or 'socoro' in nome_lower:
        return 'NOSSA SENHORA DO SOCORRO'
    elif 'itaporanga' in nome_lower:
        return "ITAPORANGA D'AJUDA"
    elif 'barra' in nome_lower and 'coqu' in nome_lower:
        return 'BARRA DOS COQUEIROS'
    elif 'japarat' in nome_lower:
        return 'JAPARATUBA'
    elif 'sao cristovao' in nome_lower or 'cristovao' in nome_lower or 'sao cris' in nome_lower:
        return 'SAO CRISTOVAO'
    elif 'neopolois' in nome_lower or 'neopolis' in nome_lower:
        return 'NEOPOLIS'
    elif 'maynard' in nome_lower:
        return 'GENERAL MAYNARD'
    elif 'santa rosa' in nome_lower:
        return 'SANTA ROSA DE LIMA'
    elif 'aracau' in nome_lower or 'aracaiu' in nome_lower:
        return 'ARACAJU'
    elif 'das flores' in nome_lower:
        return 'ILHA DAS FLORES'
    elif 'senhora apar' in nome_lower:
        return 'NOSSA SENHORA APARECIDA'
    elif 'aquibada' in nome_lower:
        return 'AQUIDABA'
    elif 'porto' in nome_lower and 'folha' in nome_lower:
        return 'PORTO DA FOLHA'
    elif 'propria' in nome_lower:
        return 'PROPRIA'
    elif 'tobias' in nome_lower:
        return 'TOBIAS BARRETO'
    elif 'estancia' in nome_lower:
        return 'ESTANCIA'
    elif 'lagarto' in nome_lower:
        return 'LAGARTO'
    elif 'itabaiana' in nome_lower and 'inha' not in nome_lower:
        return 'ITABAIANA'
    elif 'simao' in nome_lower:
        return 'SIMAO DIAS'
    
    return nome.upper()  # Retorna o nome original em maiúsculo se nenhuma regra for aplicada


def categorizar_tipo_processo(x):
    if pd.isna(x):
        return 'OUTROS'
    
    # Normalizar: pegar até hífen, unidecode e maiúsculo
    tipo = str(x).split(' - ')[0].strip() if ' - ' in str(x) else str(x).strip()
    tipo_norm = unidecode(tipo.upper())
    
    # Categorizar nas 4 principais
    if 'CIVEL' in tipo_norm or 'CIVIL' in tipo_norm:
        return 'ACAO CIVEL'
    elif 'PREVIDENCIAR' in tipo_norm:
        return 'ACAO PREVIDENCIARIA'  
    elif 'TRABALHIST' in tipo_norm:
        return 'ACAO TRABALHISTA'
    else:
        return 'OUTROS'

def normalizar_profissao(profissao_text):
    """
    Normaliza profissões de acordo com as regras específicas
    """
    if pd.isna(profissao_text) or str(profissao_text).strip() == '':
        return 'NÃO INFORMADO'
    
    # Normalizar básico: maiúsculo e sem acentos
    texto = unidecode(str(profissao_text).upper().strip())
    
    # Correções de erros óbvios
    texto = texto.replace('SEERVCOS', 'SERVICOS')
    texto = texto.replace('VENDENDOR', 'VENDEDOR')
    texto = texto.replace('ACOUGUEIRO', 'ACOUGUEIRO')
    texto = texto.replace('ACOGUEIRO', 'ACOUGUEIRO')
    texto = texto.replace('LVRADOR', 'LAVRADOR')
    texto = texto.replace('AJUNTE', 'AJUDANTE')
    texto = texto.replace('AJUNDANTE', 'AJUDANTE')
    texto = texto.replace('ATENTENDE', 'ATENDENTE')
    texto = texto.replace('MOROTISTA', 'MOTORISTA')
    texto = texto.replace('MECANCIO', 'MECANICO')
    texto = texto.replace('RECPECIONISTA', 'RECEPCIONISTA')
    texto = texto.replace('CABELEREIRA', 'CABELEIREIRA')
    texto = texto.replace('DESEMPREGAD ', 'DESEMPREGADO')
    texto = texto.replace('MONTAGEL', 'MONTAGEM')
    texto = texto.replace('SERVICO GERAIS', 'SERVICOS GERAIS')
    
    # 1. APOSENTADOS - qualquer variação vira APOSENTADO
    aposentado_variacoes = [
        'APOSENTADO', 'APOSENTADA', 'APOSNETADA', 'APOSNETADO', 
        'APOSNTADA', 'APOSSENTADA', 'APOSTADO', 'APPOSENTADA'
    ]
    for variacao in aposentado_variacoes:
        if variacao in texto:
            return 'APOSENTADO'
    
    # 2. ADMINISTRADOR
    if any(termo in texto for termo in ['ADMINISTRADOR', 'ADMINISTRADORA']):
        if 'EMPRESA' in texto:
            return 'ADMINISTRADOR DE EMPRESAS'
        else:
            return 'ADMINISTRADOR'
    
    # 3. AGENTE DE LIMPEZA
    if 'AGENTE DE LIMPEZA' in texto:
        return 'AGENTE DE LIMPEZA'
    
    # 4. TRABALHADOR RURAL (grupo grande)
    rural_termos = [
        'AGRICULTOR', 'AGRICULTORA', 'AGRICULTURA', 'AGRICUTORA',
        'LAVRADOR', 'TRABALHADOR RURAL', 'TRABALHADORA AUTONOMA',
        'TRABALHADORA RURAL', 'TRABALHORA RURAL'
    ]
    if any(termo in texto for termo in rural_termos):
        return 'TRABALHADOR RURAL'
    
    # 5. AJUDANTE
    if texto in ['AJUDANTE', 'AJUDANTE GERAL'] or texto == 'AJUDANTE':
        return 'AJUDANTE'
    elif 'AJUDANTE DE PEDREIRO' in texto:
        return 'AJUDANTE DE PEDREIRO'
    
    # 6. ARMADOR
    if 'ARMADOR' in texto:
        return 'ARMADOR'
    
    # 7. ATENDENTE DE TELEMARKETING
    if 'ATENDENTE' in texto and 'TELEMARKETING' in texto:
        return 'ATENDENTE DE TELEMARKETING'
    
    # 8. AUXILIAR - expandir AUX
    if texto.startswith('AUX ') or ' AUX ' in texto:
        # Substituir AUX por AUXILIAR
        texto = texto.replace('AUX ', 'AUXILIAR ')
        texto = texto.replace(' AUX ', ' AUXILIAR ')
        
        # Corrigir gênero para masculino (padrão)
        if 'ADMINISTRATIVA' in texto:
            texto = texto.replace('ADMINISTRATIVA', 'ADMINISTRATIVO')
        if 'AUXILIAR DE SERVICO GERAIS' in texto:
            texto = 'AUXILIAR DE SERVICOS GERAIS'
    
    # AUXILIAR - correções específicas
    if 'AUXILIAR' in texto:
        if 'SERVICOS GERAIS' in texto or 'SERVICO GERAIS' in texto:
            return 'AUXILIAR DE SERVICOS GERAIS'
        elif 'TECNICO DE MONTAGEM' in texto or 'TECNICO DE MONTAGEL' in texto:
            return 'AUXILIAR TECNICO DE MONTAGEM'
    
    # 9. BENEFICIARIO
    beneficiario_termos = [
        'BENEFICIARIA DO LOAS', 'BENEFICIARIO', 'BENEFICIARIO DO AMPARO SOCIAL',
        'BENEFICIARIO DO LOAS'
    ]
    if any(termo in texto for termo in beneficiario_termos):
        return 'BENEFICIARIO'
    
    # 10. CUIDADOR
    if any(termo in texto for termo in ['CUIDADORA', 'CUIDADOR']):
        return 'CUIDADOR'
    
    # 11. DESEMPREGADO
    if 'DESEMPREGAD' in texto:
        return 'DESEMPREGADO'
    
    # 12. MECANICO
    if 'MECANICO' in texto:
        if 'AUTOS' in texto or 'LINHA PESADA' in texto:
            return 'MECANICO'
        else:
            return 'MECANICO'
    
    # 13. MENOR
    if any(termo in texto for termo in ['MENOR DE IDADE', 'MENOR PUBERE', 'MENOR']):
        return 'MENOR'
    
    # 14. MOTORISTA
    if 'MOTORISTA' in texto:
        if 'CAMINHAO' in texto or 'BETONEIRA' in texto or 'CARRETEIRO' in texto:
            return 'MOTORISTA DE CAMINHAO'
        elif 'APLICATIVO' in texto:
            return 'MOTORISTA'
        else:
            return 'MOTORISTA'
    
    # 15. SERVENTE
    if 'SERVENTE' in texto:
        return 'SERVENTE DE PEDREIRO'
    
    # 16. SERVICOS GERAIS
    if 'SERVICOS GERAIS' in texto or 'SERVICO GERAIS' in texto:
        return 'SERVICOS GERAIS'
    
    # 17. TECNICO - expandir TEC
    if texto.startswith('TEC ') or ' TEC ' in texto or texto.startswith('TECNICO'):
        texto = texto.replace('TEC ', 'TECNICO ')
        texto = texto.replace(' TEC ', ' TECNICO ')
        
        # Manter como está, mas padronizado
        if 'TECNICO' in texto:
            return texto
    
    # 18. VENDEDOR
    if 'VENDEDOR' in texto:
        return 'VENDEDOR'
    
    # Se não encontrou padrão específico, retorna o texto limpo
    return texto