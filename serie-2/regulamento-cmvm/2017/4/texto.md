Regulamento da CMVM n.º 4/2017
Prestação de informação sobre transações em instrumentos financeiros nos termos do artigo 26.º do Regulamento (UE) n.º 600/2014 do Parlamento Europeu e do Conselho, de 15 de maio de 2014.
(Revoga a Instrução n.º 12/2011)
O presente Regulamento da Comissão do Mercado de Valores Mobiliários ("CMVM") decorre das alterações introduzidas no Código dos Valores Mobiliários ("CVM") em consequência da transposição da Diretiva n.º 2014/65/UE do Parlamento Europeu e do Conselho, de 15 de maio de 2014, relativa aos mercados de instrumentos financeiros e que altera a Diretiva n.º 2002/92/CE e a Diretiva n.º 2011/61/UE ("DMIF II"), e do Regulamento (UE) n.º 600/2014 do Parlamento Europeu e do Conselho, de 15 de maio de 2014, relativo aos mercados de instrumentos financeiros e que altera o Regulamento (UE) n.º 648/2012 ("RMIF").
O artigo 26.º do RMIF prevê que os intermediários financeiros que executem transações em instrumentos financeiros, bem como as plataformas de negociação nos casos identificados, reportam à autoridade competente as informações completas e precisas dessas transações tão rapidamente quanto possível e o mais tardar até ao fecho do dia útil seguinte, sendo tal obrigação aplicável (i) aos instrumentos financeiros admitidos à negociação ou negociados numa plataforma de negociação ou cuja admissão à negociação tenha sido solicitada, (ii) aos instrumentos financeiros cujo subjacente seja um instrumento financeiro negociado numa plataforma de negociação, e (iii) aos instrumentos financeiros cujo subjacente seja um índice ou cabaz composto por instrumentos financeiros negociados numa plataforma de negociação. Esta obrigação é aplicável a transações nos instrumentos financeiros referidos independentemente de essas transações serem ou não efetuadas na plataforma de negociação.
O reporte deve ser efetuado nos termos especificados no referido artigo 26.º do RMIF e no Regulamento Delegado (UE) n.º 2017/590 da Comissão, de 28 de julho de 2016, que complementa o RMIF no que respeita às normas técnicas de regulamentação para a comunicação de informações sobre as transações às autoridades competentes ("Regulamento UE n.º 2017/590").
Nos termos do disposto no n.º 3 do artigo 315.º do Código dos Valores Mobiliários, a CMVM pode determinar, por regulamento, os termos para a concretização da prestação de informação pelos intermediários financeiros e pelas plataformas de negociação sobre transações realizadas relativas a instrumentos financeiros.
Nesse sentido, o presente Regulamento estabelece os procedimentos e os conteúdos, conforme definidos nos documentos (Reporting Instructions, Functional Specifications e Guidelines) disponíveis para consulta no sítio da Internet da ESMA, relativos à prestação desta informação.
O modo de prestação de informação à CMVM segue os termos e condições previstos no Regulamento da CMVM n.º 3/2016, com as especificidades estabelecidas no presente Regulamento.
A informação objeto do dever de reporte deve ser remetida à CMVM em formato XML, de acordo com as especificações técnicas publicadas pela ESMA, disponíveis no sítio da Internet da CMVM. Os esquemas (.XSD) que servem de base aos ficheiros XML encontram-se disponíveis no ficheiro ZIP que integra as referidas especificações técnicas. A CMVM procede à verificação do formato XML para efeitos de deteção de erros de conteúdo.
Em complemento do referido no parágrafo anterior, é disponibilizado à entidade que procede à prestação da informação, no seu domínio da extranet, um ficheiro XML, com o mesmo nome e extensão, com o prefixo "RE_" que contém informação de sucesso ou de insucesso quanto aos ficheiros por si remetidos, nos termos definidos no Regulamento da CMVM n.º 3/2016. É da responsabilidade do intermediário financeiro ou da plataforma de negociação a confirmação sobre a aceitação do ficheiro reportado à CMVM ou a correção dos erros verificados e o envio à CMVM de ficheiros corretos.
Nestes termos, a CMVM, ao abrigo do disposto no n.º 9 do artigo 207.º, nos n.os 1 e 3 do artigo 315.º e no artigo 369.º do Código dos Valores Mobiliários, determina, através do presente Regulamento, o seguinte:
Artigo 1.º
Objeto
O presente Regulamento rege as especificidades relativas à prestação à CMVM da informação relacionada com as transações sobre instrumentos financeiros conforme previsto no RMIF e no Regulamento UE n.º 2017/590.
Artigo 2.º
Prestação de informação
1 - A informação prevista no artigo anterior é enviada à CMVM até às 23h59 m do dia útil seguinte a que se refere a informação, sendo prestada através do acesso ao domínio de extranet da CMVM, através do envio de um ficheiro informático, elaborado em conformidade com as regras de conteúdo e forma constantes dos quadros 1 e 2 do Anexo I e Anexo II ao Regulamento UE n.º 2017/590.
2 - A informação é remetida à CMVM em ficheiro de dados em formato XML, nos termos da norma ISO 20022, designado ficheiro "XTR", de acordo com as especificações técnicas publicadas pela ESMA e disponíveis no respetivo sítio da Internet:
i) Os ficheiros "XTR" são elaborados de acordo com as especificações técnicas contidas nos documentos "MiFIR transaction reporting instructions.pdf" e "2016-1521_annex_2_mifir_transaction_reporting_iso20022_xml_schemas.zip" ou em versões atualizadas dos mesmos, disponíveis no sítio da Internet da ESMA.
ii) Compete à entidade responsável pelo reporte da informação enviar o ficheiro "XTR".
iii) O conteúdo de cada ficheiro XML é coerente com a informação contida no nome do ficheiro.
iv) Os ficheiros com nomes duplicados são recusados.
v) O número máximo de transações admitido dentro de um ficheiro é de 500.000 (quinhentas mil), incluindo cancelamentos. Quando a entidade que reporta verifique a necessidade de incluir transações acima daquele limite por ficheiro, pode fazê-lo dividindo o reporte por mais ficheiros que são processados de acordo com seus respetivos números de sequência de grupo.
3 - O nome do ficheiro tem o formato "FFFNNNNNNSSSSSSXXZTTAAAAMMDD.xml" onde:
i) FFF (3 carateres) - identifica o ficheiro e é preenchido com "XTR".
ii) NNNNNN (6 algarismos) - corresponde ao código de entidade que efetua o reporte, atribuído pela CMVM, devendo ser usado o algarismo "0", à esquerda, para completar o preenchimento dos seis carateres.
iii) SSSSSS (6 algarismos) - corresponde ao número de sequência anual do ficheiro XTR, único por tipo de ficheiro e por código de entidade que efetua o reporte, atribuído pela CMVM. Começa em 000001 e reinicia todos os anos.
iv) XX (2 algarismos) - número sequencial do ficheiro em grupo ("Número sequencial").
v) Z (1 caráter) - caráter fixo separador entre Número sequencial e Número total.
vi) TT (2 algarismos) - número total de ficheiros a enviar em grupo ("Número total").
vii) AAAAMMDD (8 algarismos) - "AAAA" corresponde ao ano, "MM" ao mês e "DD" ao dia em que se está a efetuar o reporte, sendo o algarismo "0" utilizado à esquerda, para completar o preenchimento dos quatro carateres MM e DD.
Todos os carateres do nome do ficheiro são de preenchimento obrigatório.
4 - A CMVM procede à validação dos ficheiros. Os erros produzidos, decorrentes desse processo, são identificados no ficheiro "RE_", com informação detalhada dos erros detetados. Os códigos de erro, não exaustivos e que podem ser complementados, relacionados com a convenção do nome do ficheiro são os seguintes:
i) ETR-001: Wrong or invalid file name format. File name should be: FFFNNNNNNSSSSSSXXZTTAAAAMMDD.xml.
ii) ETR-002: NNNNNN is not a valid CMVM code for Reporting entity.
iii) ETR-003: SSSSSS is not a valid sequence number.
iv) ETR-004: XXZTT is not a valid code.
v) ETR-005: AAAAMMDD is not a valid date.
vi) ETR-006: NNNNNN not authorized to submit data for the executing entity.
5 - Os intermediários financeiros e as plataformas de negociação sujeitos ao dever de reporte prestam à CMVM, com uma antecedência de dois dias úteis em relação à data do primeiro reporte da informação e subsequentemente mantêm-na permanentemente atualizada, a seguinte informação:
i) Denominação social da entidade responsável pelo reporte da informação.
ii) Código do Identificador de Entidade Jurídica (código LEI) da entidade sujeita ao dever de reporte e da entidade responsável pelo reporte da informação, sendo distinta.
iii) Endereço da entidade responsável pelo reporte da informação.
iv) Contactos relevantes da entidade responsável pelo reporte da informação quando for distinta da entidade sujeita ao dever de reporte.
v) Data de início do reporte da informação e, sendo efetuado por um Sistema de Reporte Autorizado, data de fim quando predeterminado.
vi) Outras especificidades relevantes quanto às características do reporte de informação.
6 - As entidades sujeitas ao dever de reporte ou as que efetuam o reporte em nome daquelas, designadamente as plataformas de negociação e os sistemas de reporte autorizados, ainda que não se encontrem sujeitos a supervisão da CMVM, devem obter a informação necessária para o cumprimento dessa obrigação, incluindo o código de reporte atribuído pela CMVM e as permissões de acesso ao sistema de transferência de ficheiros da CMVM, conforme consta do Regulamento da CMVM n.º 3/2016.
Artigo 3.º
Entrada em vigor e regime transitório
1 - O presente Regulamento entra em vigor na data de entrada em vigor do Regulamento (UE) n.º 600/2014, do Parlamento Europeu e do Conselho, de 15 de maio de 2014, aplicando-se a todas as transações que estejam sujeitas ao dever de reporte e sejam executadas a partir dessa data, inclusive.
2 - Sem prejuízo do número seguinte, o presente Regulamento revoga a Instrução n.º 12/2011, com efeitos a partir da data indicada no número anterior.
3 - As transações executadas e reportadas até ao dia 2 de janeiro de 2018 inclusive, em que sejam detetados erros ou inconsistências, deverão ser corrigidas até ao dia 31 de janeiro de 2018 inclusive, ao abrigo da Instrução n.º 12/2011. Após essa data e relativamente a tais transações, quaisquer erros ou inconsistências deverão ser comunicados diretamente e caso a caso, à CMVM.
20 de dezembro de 2017. - A Presidente do Conselho de Administração, Gabriela Figueiredo Dias. - O Vogal do Conselho de Administração, Rui Pinto.
311021007
