Portaria n.º 363/2010
de 23 de Junho
A utilização crescente de sistemas de processamento electrónico de dados, nomeadamente para facturação da transmissão de bens ou de prestações de serviços, acarreta inegáveis vantagens em termos de celeridade do tratamento da informação.
Todavia, introduz novos riscos em termos de controlo fiscal, pela possibilidade de subsequente adulteração dos dados registados, potenciando situações de evasão fiscal.
Nesta perspectiva, importa definir regras para que os programas de facturação observem requisitos que garantam a inviolabilidade da informação inicialmente registada, permitindo-se, consequentemente, que apenas os programas que respeitem tais requisitos possam ser utilizados, após certificação pela DGCI.
Foram observados os procedimentos de notificação à Comissão Europeia previstos no Decreto-Lei n.º 58/2000, de 18 de Abril.
Assim:
Manda o Governo, ao abrigo do disposto no n.º 8 do artigo 123.º do Código do Imposto sobre o Rendimento das Pessoas Colectivas, aprovado pelo Decreto-Lei n.º 442-B/88, de 30 de Novembro, pelo Ministro de Estado e das Finanças, o seguinte:
Artigo 1.º
Objecto
A presente portaria:
a) Regulamenta a certificação prévia dos programas informáticos de facturação, a que se refere o n.º 8 do artigo 123.º do Código do Imposto sobre o Rendimento das Pessoas Colectivas, abreviadamente designado por Código do IRC, aprovado pelo Decreto-Lei n.º 442-B/88, de 30 de Novembro;
b) Altera a estrutura de dados constante do anexo à Portaria n.º 1192/2009, de 8 de Outubro.
Artigo 2.º
Certificação de programas de facturação
1 - Os programas informáticos, utilizados por sujeitos passivos de imposto sobre o rendimento das pessoas singulares (IRS) ou de imposto sobre o rendimento das pessoas colectivas (IRC), para emissão de facturas ou documentos equivalentes e talões de venda, nos termos dos artigos 36.º e 40.º do Código do Imposto sobre o Valor Acrescentado (IVA), devem ser objecto de prévia certificação pela Direcção-Geral dos Impostos (DGCI).
2 - Excluem-se do disposto no número anterior os programas de facturação utilizados por sujeitos passivos que reúnam algum dos seguintes requisitos:
a) Utilizem software produzido internamente ou por empresa integrada no mesmo grupo económico, do qual sejam detentores dos respectivos direitos de autor;
b) Tenham operações exclusivamente com clientes que exerçam actividades de produção, comércio ou prestação de serviços, incluindo os de natureza profissional;
c) Tenham tido, no período de tributação anterior, um volume de negócios inferior a (euro) 150 000;
d) Tenham emitido, no período de tributação anterior, um número de facturas, documentos equivalentes ou talões de venda inferior a 1000 unidades.
Artigo 3.º
Requisitos
A certificação dos programas de facturação depende da verificação cumulativa dos seguintes requisitos:
a) Ter a possibilidade de exportar o ficheiro a que se refere a Portaria n.º 321-A/2007, de 26 de Março;
b) Possuir um sistema que permita identificar a gravação do registo de facturas ou documentos equivalentes e talões de venda, através de um algoritmo de cifra assimétrica e de uma chave privada de conhecimento exclusivo do produtor do programa;
c) Possuir um controlo do acesso ao sistema informático, obrigando a uma autenticação de cada utilizador;
d) Não dispor de qualquer função que, no local ou remotamente, permita alterar, directa ou indirectamente, a informação de natureza fiscal, sem gerar evidência agregada à informação original.
Artigo 4.º
Obrigações
As empresas produtoras de software, antes da comercialização dos programas, para efeitos de certificação, devem enviar à DGCI:
a) Uma declaração de modelo oficial, aprovado por despacho do Ministro das Finanças;
b) A chave pública que permita validar a autenticidade e integridade do conjunto de dados a que se refere o artigo 6.º, assinados com a correspondente chave privada.
Artigo 5.º
Emissão do certificado
1 - A DGCI emite, no prazo de 30 dias a contar da recepção da declaração referida no artigo anterior, o correspondente certificado do programa.
2 - A emissão do certificado pode ser precedida de testes de conformidade devendo, para o efeito, o produtor do programa ser notificado, ficando suspenso o prazo previsto no número anterior até à conclusão dos respectivos testes.
3 - Para verificação do cumprimento dos requisitos previstos no artigo 3.º, a DGCI pode, ainda, em qualquer momento, efectuar testes de conformidade, devendo o produtor do software disponibilizar um exemplar do programa e a documentação necessária, incluindo o dicionário de dados.
4 - A DGCI mantém no seu sítio, na Internet, uma lista actualizada dos programas e respectivas versões certificadas, bem como a identificação dos produtores.
Artigo 6.º
Sistema de identificação
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
Artigo 7.º
Revogação do certificado
O membro do Governo responsável pela área das finanças, por proposta do director-geral dos Impostos, pode determinar a revogação do certificado emitido nos termos do artigo 5.º, quando deixarem de ser observados os requisitos previstos no artigo 3.º
Artigo 8.º
Alteração à Portaria n.º 1192/2009
1 - A nota técnica do campo 4.1.4.3 da estrutura de dados constante do anexo à Portaria n.º 1192/2009, de 8 de Outubro, passa a ter a seguinte redacção: «Assinatura nos termos da portaria que regulamenta a certificação dos programas informáticos de facturação. O campo deve ser preenchido com '0' (zero), caso não haja obrigatoriedade de certificação.».
2 - O formato do campo referido no número anterior passa a ser: «Texto 200».
3 - A nota técnica do campo 4.1.4.4 da referida estrutura de dados passa a ter a seguinte redacção: «Versão da chave privada utilizada na criação da assinatura do campo 4.1.4.3».
Artigo 9.º
Disposições transitórias
As empresas produtoras de software, relativamente aos programas em utilização e susceptíveis de actualização, devem apresentar, durante o mês de Setembro de 2010, a declaração a que se refere o artigo 4.º
Artigo 10.º
Obrigatoriedade de certificação
A utilização de programas certificados em conformidade com o disposto na presente portaria é obrigatória:
a) A partir de 1 de Janeiro de 2011, para os sujeitos passivos que, no ano anterior, tenham tido um volume de negócios superior a (euro) 250 000;
b) A partir de 1 de Janeiro de 2012, para os sujeitos passivos que, no ano anterior, tenham tido um volume de negócios superior a (euro) 150 000.
O Ministro de Estado e das Finanças, Fernando Teixeira dos Santos, em 7 de Maio de 2010.
