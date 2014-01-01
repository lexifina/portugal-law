# Artigo 6.º

### Sistema de identificação

1 - O sistema de identificação a que se refere a alínea b) do artigo 3.º deve utilizar o algoritmo de cifra assimétrica RSA, recebendo como argumento os seguintes dados concatenados, pela ordem indicada, com o separador «;» (ponto e vírgula), que constituem a mensagem a assinar com a chave privada, constantes da tabela 4.1 - Documentos comerciais a clientes (SalesInvoices):

a) A data de criação do documento de venda [campo 4.1.4.6 - data do documento de venda (InvoiceDate) do SAF-T (PT)];

b) A data e hora da criação do documento de venda [campo 4.1.4.11 - data de gravação do documento (SystemEntryDate) do SAF-T (PT)];

c) O número do documento de venda [campo 4.1.4.1 - identificação única do documento de venda (InvoiceNo) do SAF-T (PT)];

d) O valor do documento de venda [campo 4.1.4.19.3 - total do documento com impostos (GrossTotal) do SAF-T (PT)];

e) A assinatura gerada no documento anterior, do mesmo tipo e série de documento [campo 4.1.4.3 - chave do documento (Hash) do SAF-T (PT)].

2 - A assinatura resultante do disposto no número anterior e a versão da chave privada de encriptação devem ficar guardadas na base de dados do programa de facturação.

3 - Os documentos assinados, nos termos do n.º 1, devem conter impresso:

a) Um conjunto de quatro caracteres da assinatura a que se refere o número anterior, correspondentes à 1.ª, 11.ª, 21.ª e 31.ª posições, e separado por hífen;

b) O número do certificado atribuído ao respetivo programa, utilizando para o efeito a expressão "Processado por programa certificado n.º...";

c) A identificação única dos documentos, conforme alínea c) do n.º 1 do presente artigo e pontos iii) das alíneas a) e b) do n.º 2 do artigo seguinte.
