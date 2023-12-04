import re

# Classe representando Símbolos


class Simbolos:
    # Construtor da classe Simbolos
    def __init__(self, lexema, tipo, valor=None):
        # Atributo que armazena o lexema (nome) do símbolo
        self.lexema = lexema
        # Atributo que armazena o tipo do símbolo, como 'NUMERO' ou 'CADEIA'
        self.tipo = tipo
        # Atributo opcional que armazena o valor associado ao símbolo, inicializado como None
        self.valor = valor


class TabelaSimbolos:
    def __init__(self):
        self.simbolos = {}


class AnalisadorSemantico:
    def __init__(self):
        self.tabela_simbolos = [TabelaSimbolos()]
        self.tipos_validos = {'NUMERO': (int, float), 'CADEIA': str}

    def executar_instrucoes(self, instrucoes):
        self.tabela_simbolos.append(TabelaSimbolos())
        for instrucao in instrucoes:
            self.executar_instrucao(instrucao)
        self.tabela_simbolos.pop()

    def executar_instrucao(self, instrucao):
        if isinstance(instrucao, list):
            for i in instrucao:
                self.executar_instrucao(i)
        else:
            inst = instrucao["instrucao"]

            if inst == "BLOCO":
                self.tabela_simbolos.append(TabelaSimbolos())
            elif inst == "FIM":
                self.tabela_simbolos.pop()
            elif inst == "PRINT":
                self.processar_print(instrucao["lexema"].strip())
            elif inst in ["ATRIBUICAO", "DECLARACAO"]:
                lexema = instrucao['lexema']
                lexema = re.sub(r'^(NUMERO|CADEIA)\s*', '', lexema).strip()
                instrucao['lexema'] = lexema
                self.add_variavel(instrucao)
            else:
                print(f"ERRO: Instrução inválida '{inst}")

    def att_valor_variavel(self, lexema, valor):
        for tabela in self.tabela_simbolos:
            if lexema in tabela.simbolos:
                if tabela.simbolos[lexema].valor is not None:
                    tipo_atual = tabela.simbolos[lexema].tipo

                    if tipo_atual == 'CADEIA' and isinstance(valor, str):
                        tabela.simbolos[lexema].valor = valor
                        return
                    elif tipo_atual in ['NUMERO', 'CADEIA'] and isinstance(valor, (int, float)):
                        tabela.simbolos[lexema].valor = valor
                        return
                    else:
                        print(
                            f"ERRO de Tipo: Atribuição inválida para variável '{lexema}'")
                        return
                else:
                    print(f"ERRO: Variável '{lexema}' não declarada.")
                    return

    def add_variavel(self, instrucao):
        lexema = instrucao["lexema"].strip()
        tipo_declarado = instrucao.get("tipo_declarado")
        valor = self.processar_valor(instrucao.get("valor"))

        escopo_atual = self.tabela_simbolos[-1]

        if lexema in escopo_atual.simbolos:
            if valor is not None and isinstance(valor, self.tipos_validos[escopo_atual.simbolos[lexema].tipo]):
                escopo_atual.simbolos[lexema].valor = valor
            else:
                print(
                    f"ERRO de Tipo: Atribuição inválida para variável '{lexema}'")
        else:
            tipo_para_usar = tipo_declarado or self.inferir_tipo(valor)
            novo_simbolo = Simbolos(lexema, tipo_para_usar, valor)
            escopo_atual.simbolos[lexema] = novo_simbolo

    def processar_valor(self, valor):
        if valor is None:
            return None
        return valor.strip('"') if valor.startswith('"') and valor.endswith('"') else \
            int(valor) if valor.lstrip('-').isdigit() else \
            float(valor) if '.' in valor or valor.lstrip('-+').replace('.', '').isdigit() else \
            self.get_valor_variavel(valor.strip())

    def get_valor_variavel(self, lexema):
        for tabela in self.tabela_simbolos:
            if lexema in tabela.simbolos and tabela.simbolos[lexema].valor is not None:
                return tabela.simbolos[lexema].valor
        return None

    def inferir_tipo(self, valor):
        for nome_tipo, tipo_valido in self.tipos_validos.items():
            if isinstance(valor, tipo_valido):
                return nome_tipo
        return None

    def processar_print(self, lexema):
        tipo_variavel = self.get_tipo_variavel(lexema)
        valor_variavel = self.get_valor_variavel(lexema)

        if tipo_variavel is not None:
            print(f'PRINT <{lexema}>:\n   Tipo: {
                  tipo_variavel}\nValor: {valor_variavel}')
        else:
            print(f"ERRO: Variável '{lexema}' não declarada.")

    def get_tipo_variavel(self, lexema):
        for tabela in self.tabela_simbolos:
            if lexema in tabela.simbolos:
                return tabela.simbolos[lexema].tipo
        return None


class ProcessarSemantica:
    def processar(self, arquivo):
        with open(arquivo, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        return self.processar_codigo(conteudo)

    def processar_codigo(self, conteudo):
        instrucoes = []
        for linha in conteudo.splitlines():
            if linha.strip():
                instrucoe = self.processar_linha(linha)
                if instrucoe:
                    instrucoes.append(instrucoe)
        return instrucoes

    def processar_linha(self, linha):
        partes = linha.split(maxsplit=1)
        tipo_instrucao = partes[0]

        if tipo_instrucao == "BLOCO" or tipo_instrucao == "FIM":
            return {"instrucao": tipo_instrucao, "nome_bloco": partes[1].strip()}

        if "=" in linha:
            return self.processar_atribuicao(linha)
        elif tipo_instrucao in {"NUMERO", "CADEIA"}:
            return self.processar_declaracao(linha)
        elif tipo_instrucao == "PRINT":
            return {"instrucao": tipo_instrucao, "lexema": partes[1].strip()}

    def processar_atribuicao(self, linha):
        declaracoes = linha.split(",")
        instrucoes = []

        for declaracao in declaracoes:
            lexema, valor = [parte.strip() for parte in declaracao.split("=")]
            instrucoes.append({"instrucao": "ATRIBUICAO",
                              "lexema": lexema, "valor": valor})
        return instrucoes

    def processar_declaracao(self, linha):
        partes = linha.split(maxsplit=1)
        tipo_declarado = partes[0]
        declaracoes = [variavel.strip() for variavel in partes[1].split(",")]
        instrucoes = [{"instrucao": "DECLARACAO", "lexema": variavel,
                       "tipo_declarado": tipo_declarado} for variavel in declaracoes]
        return instrucoes


def main():
    processador = ProcessarSemantica()
    analisador = AnalisadorSemantico()

    arquivo = "teste.txt"
    instrucoes = processador.processar(arquivo)
    analisador.executar_instrucoes(instrucoes)


if __name__ == "__main__":
    main()
