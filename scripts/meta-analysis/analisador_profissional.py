#!/usr/bin/env python3
"""
ANALISADOR PROFISSIONAL META ADS
Arquitetura de Performance - ruas.dev.br
Versão 2.0: Análise completa com recomendações automáticas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

print("="*70)
print("📊 ANALISADOR PROFISSIONAL META ADS")
print("="*70)

class AnalisadorMetaProfissional:
    def __init__(self):
        self.dados = None
        self.arquivo_csv = None
        
    def encontrar_arquivo_csv(self):
        """Encontra automaticamente arquivos CSV na pasta"""
        arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
        
        if not arquivos_csv:
            print("❌ Nenhum arquivo CSV encontrado na pasta!")
            print("\n💡 Para usar:")
            print("1. Exporte do META Ads Manager como CSV")
            print("2. Salve o arquivo nesta pasta")
            print("3. Execute novamente")
            return None
        
        # Priorizar arquivos com nomes comuns
        for nome in ['dados_meta.csv', 'meta_ads.csv', 'relatorio.csv', 'ads_data.csv']:
            if nome in arquivos_csv:
                return nome
        
        return arquivos_csv[0]
    
    def carregar_dados(self):
        """Carrega e prepara os dados"""
        print("\n📥 CARREGANDO DADOS...")
        
        self.arquivo_csv = self.encontrar_arquivo_csv()
        if not self.arquivo_csv:
            return False
        
        print(f"✅ Arquivo: {self.arquivo_csv}")
        
        try:
            # Ler CSV
            self.dados = pd.read_csv(self.arquivo_csv)
            print(f"✅ {len(self.dados)} linhas carregadas")
            
            # Padronizar nomes de colunas
            self._padronizar_colunas()
            
            # Converter tipos de dados
            self._converter_tipos()
            
            # Adicionar colunas calculadas
            self._adicionar_colunas_calculadas()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def _padronizar_colunas(self):
        """Padroniza nomes de colunas em português"""
        mapeamento = {}
        
        for col in self.dados.columns:
            col_lower = str(col).lower()
            
            if 'date' in col_lower or 'data' in col_lower:
                mapeamento[col] = 'Data'
            elif 'camp' in col_lower:
                mapeamento[col] = 'Campanha'
            elif 'spend' in col_lower or 'gasto' in col_lower or 'amount' in col_lower or 'custo' in col_lower:
                mapeamento[col] = 'Gasto'
            elif 'lead' in col_lower or 'result' in col_lower or 'convers' in col_lower:
                mapeamento[col] = 'Leads'
            elif 'click' in col_lower:
                mapeamento[col] = 'Cliques'
            elif 'impress' in col_lower:
                mapeamento[col] = 'Impressoes'
            elif 'reach' in col_lower or 'alcance' in col_lower:
                mapeamento[col] = 'Alcance'
            elif 'cpm' in col_lower:
                mapeamento[col] = 'CPM'
            elif 'cpc' in col_lower:
                mapeamento[col] = 'CPC'
        
        if mapeamento:
            self.dados = self.dados.rename(columns=mapeamento)
            print(f"📋 Colunas padronizadas: {list(self.dados.columns)}")
    
    def _converter_tipos(self):
        """Converte tipos de dados"""
        # Converter Data para datetime
        if 'Data' in self.dados.columns:
            self.dados['Data'] = pd.to_datetime(self.dados['Data'], errors='coerce')
        
        # Converter colunas numéricas
        colunas_numericas = ['Gasto', 'Leads', 'Cliques', 'Impressoes', 'Alcance', 'CPM', 'CPC']
        for col in colunas_numericas:
            if col in self.dados.columns:
                self.dados[col] = pd.to_numeric(self.dados[col], errors='coerce').fillna(0)
    
    def _adicionar_colunas_calculadas(self):
        """Adiciona colunas calculadas"""
        if 'Gasto' in self.dados.columns and 'Leads' in self.dados.columns:
            self.dados['CAC'] = np.where(
                self.dados['Leads'] > 0,
                self.dados['Gasto'] / self.dados['Leads'],
                0
            )
        
        if 'Cliques' in self.dados.columns and 'Impressoes' in self.dados.columns:
            self.dados['CTR'] = np.where(
                self.dados['Impressoes'] > 0,
                (self.dados['Cliques'] / self.dados['Impressoes']) * 100,
                0
            )
        
        if 'Cliques' in self.dados.columns and 'Leads' in self.dados.columns:
            self.dados['Taxa_Conversao'] = np.where(
                self.dados['Cliques'] > 0,
                (self.dados['Leads'] / self.dados['Cliques']) * 100,
                0
            )
    
    def analisar_periodo(self, periodo_dias=7):
        """Analisa um período específico"""
        if self.dados is None or self.dados.empty:
            return None
        
        # Filtrar últimos N dias
        if 'Data' in self.dados.columns:
            data_limite = datetime.now() - timedelta(days=periodo_dias)
            dados_periodo = self.dados[self.dados['Data'] >= data_limite].copy()
        else:
            dados_periodo = self.dados.tail(periodo_dias).copy()
        
        # Calcular métricas do período
        resultados = {
            'dias': len(dados_periodo),
            'gasto_total': dados_periodo['Gasto'].sum() if 'Gasto' in dados_periodo.columns else 0,
            'leads_total': dados_periodo['Leads'].sum() if 'Leads' in dados_periodo.columns else 0,
            'cliques_total': dados_periodo['Cliques'].sum() if 'Cliques' in dados_periodo.columns else 0,
            'impressoes_total': dados_periodo['Impressoes'].sum() if 'Impressoes' in dados_periodo.columns else 0,
        }
        
        # Calcular médias
        if resultados['dias'] > 0:
            resultados['gasto_diario'] = resultados['gasto_total'] / resultados['dias']
            resultados['leads_diario'] = resultados['leads_total'] / resultados['dias']
            resultados['cac_medio'] = resultados['gasto_total'] / resultados['leads_total'] if resultados['leads_total'] > 0 else 0
            resultados['ctr_medio'] = (resultados['cliques_total'] / resultados['impressoes_total'] * 100) if resultados['impressoes_total'] > 0 else 0
        
        return resultados
    
    def gerar_relatorio_completo(self):
        """Gera relatório completo com análise"""
        if self.dados is None:
            print("❌ Nenhum dado carregado!")
            return
        
        print("\n" + "="*70)
        print("📈 RELATÓRIO COMPLETO DE PERFORMANCE")
        print("="*70)
        
        # Análises por período
        periodos = [
            ('HOJE', 1),
            ('ÚLTIMOS 7 DIAS', 7),
            ('ÚLTIMOS 30 DIAS', 30),
            ('TODO PERÍODO', len(self.dados))
        ]
        
        for nome_periodo, dias in periodos:
            analise = self.analisar_periodo(dias)
            if analise and analise['dias'] > 0:
                print(f"\n📊 {nome_periodo}:")
                print("-"*40)
                print(f"   • Dias analisados: {analise['dias']}")
                print(f"   • Gasto Total: R$ {analise['gasto_total']:,.2f}")
                print(f"   • Leads Total: {analise['leads_total']:.0f}")
                print(f"   • CAC Médio: R$ {analise.get('cac_medio', 0):,.2f}")
                print(f"   • CTR Médio: {analise.get('ctr_medio', 0):.2f}%")
                
                if 'gasto_diario' in analise:
                    print(f"   • Média/dia: R$ {analise['gasto_diario']:,.2f} | {analise['leads_diario']:.1f} leads")
        
        # Análise por campanha (top 5)
        if 'Campanha' in self.dados.columns:
            print(f"\n🏆 TOP 5 CAMPANHAS (por Leads):")
            print("-"*40)
            
            top_campanhas = self.dados.groupby('Campanha').agg({
                'Gasto': 'sum',
                'Leads': 'sum',
                'Cliques': 'sum'
            }).reset_index()
            
            top_campanhas['CAC'] = top_campanhas['Gasto'] / top_campanhas['Leads'].replace(0, np.nan)
            top_campanhas = top_campanhas.sort_values('Leads', ascending=False).head(5)
            
            for idx, row in top_campanhas.iterrows():
                print(f"   {row['Campanha'][:30]:30} | {row['Leads']:.0f} leads | CAC: R$ {row['CAC']:,.2f}")
        
        # Tendências
        if 'Data' in self.dados.columns and len(self.dados) >= 3:
            print(f"\n📈 TENDÊNCIA (últimos 3 dias vs anterior):")
            print("-"*40)
            
            if len(self.dados) >= 6:
                ultimos_3 = self.dados.tail(3)
                anteriores_3 = self.dados.iloc[-6:-3]
                
                if not anteriores_3.empty:
                    cac_ultimos = ultimos_3['Gasto'].sum() / ultimos_3['Leads'].sum() if ultimos_3['Leads'].sum() > 0 else 0
                    cac_anteriores = anteriores_3['Gasto'].sum() / anteriores_3['Leads'].sum() if anteriores_3['Leads'].sum() > 0 else 0
                    
                    variacao_cac = ((cac_ultimos - cac_anteriores) / cac_anteriores * 100) if cac_anteriores > 0 else 0
                    
                    seta = "🔼" if variacao_cac > 0 else "🔽" if variacao_cac < 0 else "➡️"
                    print(f"   • CAC: {seta} {variacao_cac:+.1f}%")
        
        # Recomendações automáticas
        print(f"\n💡 RECOMENDAÇÕES AUTOMÁTICAS:")
        print("-"*40)
        
        # Analisar últimos 7 dias para recomendações
        analise_7dias = self.analisar_periodo(7)
        
        if analise_7dias and analise_7dias.get('cac_medio', 0) > 0:
            cac = analise_7dias['cac_medio']
            
            if cac > 80:
                print("   ⚠️  CAC MUITO ALTO (> R$ 80)")
                print("      • Reduza orçamento de campanhas ineficientes")
                print("      • Reveja segmentação e criativos")
                print("      • Considere pausar campanhas problemáticas")
            elif cac > 50:
                print("   ⚠️  CAC ALTO (R$ 50-80)")
                print("      • Otimize lances e orçamentos")
                print("      • Teste novas audiências")
                print("      • Melhore landing pages")
            elif cac > 20:
                print("   ✅ CAC RAZOÁVEL (R$ 20-50)")
                print("      • Mantenha estratégia atual")
                print("      • Pequenos ajustes de otimização")
                print("      • Escale campanhas com melhor ROI")
            else:
                print("   🎉 CAC EXCELENTE (< R$ 20)")
                print("      • AUMENTE ORÇAMENTO")
                print("      • Duplique campanhas vencedoras")
                print("      • Expanda para novas audiências")
        
        # Verificar CTR
        if analise_7dias and analise_7dias.get('ctr_medio', 0) > 0:
            ctr = analise_7dias['ctr_medio']
            
            if ctr < 1:
                print("\n   ⚠️  CTR BAIXO (< 1%)")
                print("      • Teste novos criativos")
                print("      • Melhore copy e headlines")
                print("      • Ajuste segmentação")
            elif ctr > 3:
                print("\n   ✅ CTR ALTO (> 3%)")
                print("      • Criativos funcionando bem!")
                print("      • Mantenha ou teste variações")
        
        # Previsão do mês
        if analise_7dias and analise_7dias.get('leads_diario', 0) > 0:
            leads_diario = analise_7dias['leads_diario']
            gasto_diario = analise_7dias.get('gasto_diario', 0)
            
            print(f"\n🔮 PREVISÃO MENSAL (baseado em média diária):")
            print(f"   • Leads/mês: {leads_diario * 30:.0f}")
            print(f"   • Gasto/mês: R$ {gasto_diario * 30:,.2f}")
            print(f"   • CAC estimado: R$ {analise_7dias.get('cac_medio', 0):,.2f}")
        
        print("\n" + "="*70)
        print("✅ RELATÓRIO GERADO COM SUCESSO!")
        print("="*70)
    
    def exportar_relatorio_detalhado(self, nome_arquivo="relatorio_detalhado.csv"):
        """Exporta relatório detalhado para CSV"""
        if self.dados is None:
            return False
        
        try:
            # Criar relatório resumido
            relatorio = self.dados.copy()
            
            # Se tiver muitos dados, resumir por dia
            if 'Data' in relatorio.columns and len(relatorio) > 10:
                relatorio['Data'] = pd.to_datetime(relatorio['Data']).dt.date
                relatorio = relatorio.groupby('Data').agg({
                    'Gasto': 'sum',
                    'Leads': 'sum',
                    'Cliques': 'sum',
                    'Impressoes': 'sum',
                    'CAC': 'mean',
                    'CTR': 'mean',
                    'Taxa_Conversao': 'mean'
                }).reset_index()
            
            # Salvar CSV
            relatorio.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
            print(f"\n💾 Relatório detalhado salvo: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar relatório: {e}")
            return False
    
    def salvar_metricas_chave(self, nome_arquivo="metricas_chave.txt"):
        """Salva métricas chave em arquivo de texto"""
        if self.dados is None:
            return False
        
        try:
            analise_7dias = self.analisar_periodo(7)
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("📊 MÉTRICAS CHAVE META ADS\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write(f"Arquivo analisado: {self.arquivo_csv}\n\n")
                
                if analise_7dias:
                    f.write("📈 ÚLTIMOS 7 DIAS:\n")
                    f.write(f"• Gasto Total: R$ {analise_7dias['gasto_total']:,.2f}\n")
                    f.write(f"• Leads Total: {analise_7dias['leads_total']:.0f}\n")
                    f.write(f"• CAC Médio: R$ {analise_7dias.get('cac_medio', 0):,.2f}\n")
                    f.write(f"• CTR Médio: {analise_7dias.get('ctr_medio', 0):.2f}%\n")
                    f.write(f"• Média/dia: {analise_7dias.get('leads_diario', 0):.1f} leads\n\n")
                
                f.write("🎯 RECOMENDAÇÕES:\n")
                if analise_7dias and analise_7dias.get('cac_medio', 0) > 50:
                    f.write("- CAC alto: Otimizar campanhas e revisar segmentação\n")
                elif analise_7dias and analise_7dias.get('cac_medio', 0) < 20:
                    f.write("- CAC excelente: Aumentar orçamento das melhores campanhas\n")
            
            print(f"📝 Métricas chave salvas: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar métricas: {e}")
            return False

# ================= PROGRAMA PRINCIPAL =================
def main():
    """Função principal"""
    print("🚀 Iniciando Analisador Profissional META Ads...\n")
    
    # Criar analisador
    analisador = AnalisadorMetaProfissional()
    
    # Carregar dados
    if not analisador.carregar_dados():
        print("\n💡 DICA: Exporte seus dados do META Ads como CSV e salve na pasta.")
        return
    
    # Gerar relatório completo
    analisador.gerar_relatorio_completo()
    
    # Exportar relatórios
    analisador.exportar_relatorio_detalhado()
    analisador.salvar_metricas_chave()
    
    print("\n🎉 ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("📊 Use os insights para tomar decisões estratégicas")
    print("🌐 Arquitetura de Performance - ruas.dev.br")

if __name__ == "__main__":
    main()
