#!/usr/bin/env python3
"""
ANALISADOR DE LEADS META ADS - PORTUGUÊS
Autor: Irving - Arquitetura de Performance
Site: ruas.dev.br
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

print("="*60)
print("📊 ANALISADOR DE LEADS META ADS")
print("="*60)

class AnalisadorMetaAds:
    def __init__(self, arquivo_csv=None):
        self.arquivo_csv = arquivo_csv
        self.dados = None

    def carregar_dados(self):
        """Carrega dados do CSV do META Ads"""
        print("\n1️⃣ CARREGANDO DADOS...")

        if not self.arquivo_csv or not os.path.exists(self.arquivo_csv):
            # Procurar qualquer arquivo CSV na pasta
            arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
            if not arquivos_csv:
                print("❌ Nenhum arquivo CSV encontrado!")
                return False

            self.arquivo_csv = arquivos_csv[0]

        print(f"✅ Arquivo: {self.arquivo_csv}")

        try:
            # Ler o CSV
            self.dados = pd.read_csv(self.arquivo_csv)
            print(f"✅ Linhas carregadas: {len(self.dados)}")

            # Mostrar colunas disponíveis
            print(f"📋 Colunas encontradas: {list(self.dados.columns)}")

            # Padronizar nomes das colunas (português/inglês)
            mapeamento_colunas = {
                'Data': 'Data',
                'Date': 'Data',
                'Campaign': 'Campanha',
                'Campaign name': 'Campanha',
                'Nome da campanha': 'Campanha',
                'Impressions': 'Impressoes',
                'Impressões': 'Impressoes',
                'Clicks': 'Cliques',
                'Cliques': 'Cliques',
                'Spend': 'Gasto',
                'Gasto': 'Gasto',
                'Amount spent': 'Gasto',
                'Leads': 'Leads',
                'Resultados': 'Leads',
                'Results': 'Leads'
            }

            # Renomear colunas
            for col_antiga, col_nova in mapeamento_colunas.items():
                if col_antiga in self.dados.columns:
                    self.dados = self.dados.rename(columns={col_antiga: col_nova})

            # Converter Data para datetime
            if 'Data' in self.dados.columns:
                self.dados['Data'] = pd.to_datetime(self.dados['Data'])

            # Garantir que colunas numéricas sejam números
            colunas_numericas = ['Impressoes', 'Cliques', 'Gasto', 'Leads']
            for col in colunas_numericas:
                if col in self.dados.columns:
                    self.dados[col] = pd.to_numeric(self.dados[col], errors='coerce').fillna(0)

            return True

        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False

    def calcular_metricas(self):
        """Calcula todas as métricas importantes"""
        if self.dados is None or self.dados.empty:
            print("❌ Nenhum dado para analisar!")
            return None

        print("\n2️⃣ CALCULANDO MÉTRICAS...")

        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)

        # Converter datas para comparar
        if 'Data' in self.dados.columns:
            self.dados['Data_date'] = pd.to_datetime(self.dados['Data']).dt.date

        # DADOS DE HOJE (se existir na planilha)
        dados_hoje = self.dados[self.dados['Data_date'] == hoje] if 'Data_date' in self.dados.columns else pd.DataFrame()

        # DADOS DE ONTEM
        dados_ontem = self.dados[self.dados['Data_date'] == ontem] if 'Data_date' in self.dados.columns else self.dados.tail(1)

        # ÚLTIMOS 7 DIAS
        sete_dias_atras = hoje - timedelta(days=7)
        if 'Data_date' in self.dados.columns:
            dados_7dias = self.dados[self.dados['Data_date'] >= sete_dias_atras]
        else:
            dados_7dias = self.dados.tail(7)

        # ESTE MÊS (desde o dia 1)
        inicio_mes = hoje.replace(day=1)
        if 'Data_date' in self.dados.columns:
            dados_mes = self.dados[self.dados['Data_date'] >= inicio_mes]
        else:
            dados_mes = self.dados

        # CALCULAR TOTAIS
        def calcular_totais(df):
            return {
                'Gasto': df['Gasto'].sum() if 'Gasto' in df.columns else 0,
                'Leads': df['Leads'].sum() if 'Leads' in df.columns else 0,
                'Cliques': df['Cliques'].sum() if 'Cliques' in df.columns else 0,
                'Impressoes': df['Impressoes'].sum() if 'Impressoes' in df.columns else 0
            }

        totais_hoje = calcular_totais(dados_hoje)
        totais_ontem = calcular_totais(dados_ontem)
        totais_7dias = calcular_totais(dados_7dias)
        totais_mes = calcular_totais(dados_mes)

        # CALCULAR MÉTRICAS
        def calcular_cac(gasto, leads):
            return gasto / leads if leads > 0 else 0

        def calcular_ctr(cliques, impressoes):
            return (cliques / impressoes * 100) if impressoes > 0 else 0

        def calcular_taxa_conversao(leads, cliques):
            return (leads / cliques * 100) if cliques > 0 else 0

        # Resultados
        metricas = {
            'hoje': {
                'gasto': totais_hoje['Gasto'],
                'leads': totais_hoje['Leads'],
                'cac': calcular_cac(totais_hoje['Gasto'], totais_hoje['Leads']),
                'ctr': calcular_ctr(totais_hoje['Cliques'], totais_hoje['Impressoes']),
                'taxa_conversao': calcular_taxa_conversao(totais_hoje['Leads'], totais_hoje['Cliques'])
            },
            'ontem': {
                'gasto': totais_ontem['Gasto'],
                'leads': totais_ontem['Leads'],
                'cac': calcular_cac(totais_ontem['Gasto'], totais_ontem['Leads'])
            },
            '7_dias': {
                'gasto': totais_7dias['Gasto'],
                'leads': totais_7dias['Leads'],
                'cac': calcular_cac(totais_7dias['Gasto'], totais_7dias['Leads']),
                'ctr': calcular_ctr(totais_7dias['Cliques'], totais_7dias['Impressoes']),
                'taxa_conversao': calcular_taxa_conversao(totais_7dias['Leads'], totais_7dias['Cliques']),
                'dias': len(dados_7dias)
            },
            'mes': {
                'gasto': totais_mes['Gasto'],
                'leads': totais_mes['Leads'],
                'cac': calcular_cac(totais_mes['Gasto'], totais_mes['Leads']),
                'dias': len(dados_mes)
            }
        }

        # Calcular variação vs ontem
        if metricas['ontem']['leads'] > 0:
            variacao_leads = ((metricas['hoje']['leads'] - metricas['ontem']['leads']) / metricas['ontem']['leads']) * 100
        else:
            variacao_leads = 100 if metricas['hoje']['leads'] > 0 else 0

        metricas['variacao'] = {
            'leads': variacao_leads,
            'cac': metricas['hoje']['cac'] - metricas['ontem']['cac'],
            'gasto': metricas['hoje']['gasto'] - metricas['ontem']['gasto']
        }

        # Médias diárias
        metricas['7_dias']['media_diaria'] = {
            'gasto': metricas['7_dias']['gasto'] / metricas['7_dias']['dias'] if metricas['7_dias']['dias'] > 0 else 0,
            'leads': metricas['7_dias']['leads'] / metricas['7_dias']['dias'] if metricas['7_dias']['dias'] > 0 else 0
        }

        metricas['mes']['media_diaria'] = {
            'gasto': metricas['mes']['gasto'] / metricas['mes']['dias'] if metricas['mes']['dias'] > 0 else 0,
            'leads': metricas['mes']['leads'] / metricas['mes']['dias'] if metricas['mes']['dias'] > 0 else 0
        }

        # Previsão do mês (baseado na média)
        dias_no_mes = 30
        metricas['previsao_mes'] = {
            'leads': metricas['mes']['media_diaria']['leads'] * dias_no_mes,
            'gasto': metricas['mes']['media_diaria']['gasto'] * dias_no_mes,
            'cac': metricas['mes']['cac']
        }

        print("✅ Métricas calculadas!")
        return metricas

    def gerar_relatorio(self, metricas):
        """Gera relatório formatado"""
        print("\n" + "="*60)
        print("📈 RELATÓRIO COMPLETO - META ADS")
        print("="*60)

        print(f"\n📍 DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print("-"*50)

        # HOJE
        print("\n🎯 HOJE:")
        print(f"   • Gasto: R$ {metricas['hoje']['gasto']:,.2f}")
        print(f"   • Leads: {int(metricas['hoje']['leads'])}")
        print(f"   • CAC: R$ {metricas['hoje']['cac']:,.2f}")
        print(f"   • CTR: {metricas['hoje']['ctr']:.2f}%")
        print(f"   • Conversão: {metricas['hoje']['taxa_conversao']:.2f}%")
#!/usr/bin/env python3
"""
ANALISADOR DE LEADS META ADS - PORTUGUÊS
Versão SIMPLIFICADA para teste
"""

print("="*60)
print("📊 ANALISADOR DE LEADS META ADS")
print("="*60)

print("\n🧪 TESTANDO SE TUDO FUNCIONA...")

# Tentar importar pandas
try:
    import pandas as pd
    print("✅ Pandas importado com sucesso!")
except ImportError:
    print("❌ Pandas não instalado!")
    print("💡 Execute: pip install pandas")
    exit()

print("\n📁 BUSCANDO ARQUIVOS CSV...")

import os

# Procurar arquivos CSV
arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]

if not arquivos_csv:
    print("❌ Nenhum arquivo CSV encontrado!")
    print("💡 Criando arquivo de teste...")

    # Criar dados de exemplo
    dados_exemplo = """Data,Campanha,Impressoes,Cliques,Gasto,Leads
2024-12-01,Campanha Educação,10000,500,250.00,25
2024-12-02,Campanha Educação,12000,600,300.00,30
2024-12-03,Campanha Educação,11000,550,275.00,28
2024-12-04,Campanha Educação,13000,650,325.00,32
2024-12-05,Campanha Educação,14000,700,350.00,35
2024-12-06,Campanha Educação,15000,750,375.00,38"""

    with open('dados_teste.csv', 'w') as f:
        f.write(dados_exemplo)

    print("✅ Arquivo 'dados_teste.csv' criado!")
    arquivo_csv = 'dados_teste.csv'
else:
    arquivo_csv = arquivos_csv[0]
    print(f"✅ Arquivo encontrado: {arquivo_csv}")

# Ler o CSV
print(f"\n📊 LENDO ARQUIVO: {arquivo_csv}")
try:
    df = pd.read_csv(arquivo_csv)
    print(f"✅ Dados carregados: {len(df)} linhas")
    print(f"📋 Colunas: {list(df.columns)}")

    # Mostrar primeiras linhas
    print("\n📄 PRIMEIRAS LINHAS:")
    print(df.head())

    # Calcular totais básicos
    if 'Gasto' in df.columns:
        gasto_total = df['Gasto'].sum()
        print(f"\n💰 GASTO TOTAL: R$ {gasto_total:,.2f}")

    if 'Leads' in df.columns:
        leads_total = df['Leads'].sum()
        print(f"👥 LEADS TOTAL: {leads_total}")

    if 'Gasto' in df.columns and 'Leads' in df.columns:
        cac = gasto_total / leads_total if leads_total > 0 else 0
        print(f"🎯 CAC (Custo por Lead): R$ {cac:,.2f}")

    if 'Cliques' in df.columns and 'Impressoes' in df.columns:
        ctr = (df['Cliques'].sum() / df['Impressoes'].sum() * 100) if df['Impressoes'].sum() > 0 else 0
        print(f"🖱️  CTR: {ctr:.2f}%")

    # Salvar relatório simples
    print("\n💾 SALVANDO RELATÓRIO...")
    df.to_csv('relatorio_simples.csv', index=False, encoding='utf-8-sig')
    print("✅ Relatório salvo: 'relatorio_simples.csv'")

except Exception as e:
    print(f"❌ Erro ao processar CSV: {e}")

print("\n" + "="*60)
print("✅ TESTE CONCLUÍDO COM SUCESSO!")
print("="*60)

print("\n🎯 PRÓXIMOS PASSOS:")
print("1. Exporte SEUS dados do META Ads como CSV")
print("2. Substitua 'dados_teste.csv' pelo seu arquivo")
print("3. Execute: python3 analisador_meta.py")
print("\n📞 Dúvidas? Irving - ruas.dev.br")
