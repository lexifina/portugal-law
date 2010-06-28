# Artigo 6.º

### Sistema de identificação

1 - O sistema de identificação a que se refere a alínea b) do artigo 3.º deve utilizar o algoritmo de cifra assimétrica RSA, recebendo como argumento os seguintes dados concatenados, pela ordem indicada, com o separador «;» (ponto e vírgula), que constituem a mensagem a assinar com a chave privada:

a) A data de criação da factura, do documento equivalente ou do talão de venda [campo 4.1.4.6 - data do documento de venda (JnvoiceDate) do SAF-T (PT)];

b) A data e hora da última alteração da factura, do documento equivalente ou do talão de venda [campo 4.1.4.9 - data de gravação do documento (SystemEntryDate) do SAF-T (PT)];

c) O número da factura, do documento equivalente ou do talão de venda [campo 4.1.4.1 - identificação única do documento de venda (JnvoiceNo) do SAF-T (PT)];

d) O valor da factura, do documento equivalente ou do talão de venda [campo 4.1.4.15.3 - total do documento com impostos (GrossTotal) do SAF-T (PT)];

e) A assinatura gerada no documento anterior, da mesma série [campo 4.1.4.3 - chave do documento (Hash) do SAF-T (PT)].

2 - A assinatura resultante do disposto no número anterior e a versão da chave privada de encriptação devem ficar guardadas na base de dados do programa de facturação.

3 - As facturas ou documentos equivalentes e os talões de venda devem conter impresso:

a) Um conjunto de quatro caracteres da assinatura a que se refere o número anterior, correspondentes à 1.ª, 11.ª, 21.ª e 31.ª posições, e separado por hífen;

b) O número do certificado atribuído ao respectivo programa, utilizando para o efeito a expressão «Processado por programa certificado n.º ...», que substitui a prevista no n.º 3 do artigo 8.º do regime de bens em circulação, aprovado pelo Decreto-Lei n.º 147/2003, de 11 de Julho.
