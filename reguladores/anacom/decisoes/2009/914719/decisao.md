# Especificação de Portabilidade

Decisão de 2009-04-15 · publicado em 2009-04-17

Por deliberação de 15 de Abril de 2009, a ANACOM aprovou a Especificação de Portabilidade alterada, bem como a respectiva nota justificativa.

Especificação de Portabilidade

Nota Justificativa

1. Enquadramento

2. Análise das alterações introduzidas na Especificação

3. Outros assuntos

4. Deliberação

1. Enquadramento

O Regulamento da Portabilidade n.º 87/2009, de 18 de Fevereiro, (Regulamento), aprovado a 4 de Fevereiro de 2009 pelo Conselho de Administração do ICP-ANACOM, ao mesmo tempo que altera o Regulamento n.º 58/2005, de 18 de Agosto, introduz, nomeadamente, o artigo 4.º, onde é definida a forma do Regulamento entrar em vigor. Assim, no n.º 2 deste artigo é determinado que ''Os anexos I e II da Especificação de Portabilidade devem ser revistos e actualizados pelas empresas com obrigação de portabilidade e pela Entidade de Referência com a coordenação do ICP-ANACOM e disponibilizados no sítio desta Autoridade na Internet no prazo máximo de 2 meses após a publicação do Regulamento''.

Para dar cumprimento ao disposto, o ICP-ANACOM enviou um ofício, a 23 de Fevereiro, a todos os prestadores com obrigações de portabilidade e à Entidade de Referência (ER), convocando-os para duas reuniões, no sentido de dar início aos trabalhos da actualização dos referidos anexos I e II, conforme disposto no Regulamento da Portabilidade.

Neste contexto, realizaram-se seis reuniões de trabalho que tiveram lugar nos dias 10, 11, 23 e 24 de Março e 6 e 7 de Abril com as empresas que aceitaram participar nas mesmas, três reuniões do Grupo de Trabalho para o Interface Técnico entre Redes (GTIR), para analisar e especificar as alterações relativas ao anexo I, e três reuniões do Grupo de Trabalho para os Processos Administrativos (GTPA), para o mesmo efeito para o anexo II.

No decurso das reuniões debateram-se diferentes formas de operacionalizar as alterações efectuadas no Regulamento n.º 58/2005 - Regulamento da Portabilidade -, tendo sido apresentados diversos contributos pelas empresas, bem como as suas posições, interesses e constrangimentos quando se impunha escolher entre diversas opções.

Assim, quando a norma do regulamento permitia várias soluções de normalização técnica para a especificação e não existia acordo quanto à solução a ser adoptada entre as empresas, o ICP-ANACOM ponderava os diversos argumentos e interesses apresentados, e optava, em geral, tendo em conta a posição da maioria das empresas em presença. Deste processo existe registo nas actas das reuniões, cujas minutas foram aprovadas pelas empresas que tomaram parte nessas reuniões.

A análise que a seguir se apresenta expõe, de uma forma resumida, as alterações mais significativas efectuadas na Especificação - anexo I e anexo II -, e apresenta ainda a fundamentação para a opção escolhida, para as situações onde não foi atingido o acordo entre as empresas.

2. Análise das alterações introduzidas na Especificação

Em primeiro lugar, a Especificação aprovada e publicada pelo ICP-ANACOM data de 2001. Contudo, sendo a especificação constituída por dois documentos eminentemente técnicos e operacionais, eles ganharam, na prática, uma autonomia própria e sofreram actualizações em resultado de melhoramentos, ou simples ajustamentos, que eram propostos, partilhados e difundidos entre os interessados - prestadores com obrigações de portabilidade e Entidade de Referência (ER) -, mas que não foram publicados no sítio do ICP-ANACOM.

De facto, ao definir-se a Especificação da Portabilidade no respectivo Regulamento, aprovado e publicado em 2005, como o conjunto de regras de carácter técnico e procedimental aprovado por deliberação do Conselho de Administração do ICP-ANACOM de 28 de Junho de 2001, ao mesmo tempo autonomizou-se esse conjunto de regras, por estar previsto na mesma definição ''…sem prejuízo de alterações que venham a ser introduzidas sempre que tal seja conveniente''. Contava-se que, sendo a especificação um documento operacional e ''vivo'', requereria uma maior dinâmica no processo de aprovação/conciliação, dificilmente compatível com a maior estabilidade pretendida para uma norma regulamentar, no caso, um regulamento.

Como a prática mostrou, estes documentos técnicos sofreram alterações e aditamentos que, não estando embora publicados na sua última versão no sítio do ICP-ANACOM, em nada perturbaram o bom desempenho geral das empresas na execução da portabilidade.

Assim, os documentos que constituem a nova Especificação da Portabilidade contêm, não só as modificações decorrentes das alterações do Regulamento, mas também as actualizações que foram sendo implementadas pelos prestadores e pela ER desde 2001.

Tendo cada documento da Especificação - anexo I e anexo II - sido analisado no seu grupo de trabalho próprio - GTIR e GTPA - a análise das alterações introduzidas é efectuada em separado.

2.1 Análise do Anexo I - Interface Técnico entre Redes

A alteração com maior impacto nesta especificação deriva da exigência de acomodar a situação de previsão da extinção de serviço por parte de uma empresa.

Embora o Regulamento tenha definido um conjunto de princípios, regras e condições associadas à extinção do serviço, não determinou o modo de implementar essas regras. Para operacionalizar a extinção de serviço foram identificados 4 cenários.

2.1.1 Análise de cenários

Foram identificados quatro cenários possíveis, tendo merecido maior interesse os cenários 3 e 4. O cenário 3, que decorria directamente do Regulamento, pressupunha:

As chamadas destinadas a números dos blocos de numeração atribuídos à empresa que extingue o serviço utilizam a metodologia de pesquisa prévia para encaminhamento All Call Query (ACQ), eliminando assim a necessidade de ser gerada a libertação da chamada com causa n.º 14 (REL#14);

Os números activos dos blocos de numeração são considerados sempre portados;

Os números não activos, bem como os números que venham a ser desactivados por desactivação do serviço pelo cliente, e após período de quarentena1, são devolvidos ao ICP-ANACOM, ficando indisponíveis2 no PNN, para atribuição.

O cenário 4 pressupunha:

Os blocos de numeração atribuídos à empresa que extingue o serviço são atribuídos a outra empresa através de um processo de selecção, na base do maior volume de números portados dos blocos de numeração daquela empresa (números ported-out). Este cenário apresentou-se sob duas variantes, uma, em que o cálculo dos números portados é feito na base do volume total, e outra, em que cada bloco da empresa com serviço extinto é tratado em separado, sendo a sua reatribuição efectuada à empresa em condições de elegibilidade (maior volume de números ported-out) para esse mesmo bloco.

Porque este cenário não satisfazia o requisito de responder rapidamente a uma situação de extinção, em particular porque causava interrupção de serviço aos clientes com números da empresa extinta, mas que não eram já clientes dessa empresa à data da extinção, o ICP-ANACOM considerou que, a optar-se pelo cenário 4, seria necessário adicionalmente, no momento da extinção, um cenário do tipo 3. Assim, devia ser prevista a existência de um período transitório coincidente com o período de quarentena, onde as chamadas seriam encaminhadas sem recurso à recepção do REL#14.

Após o período de quarentena e com a escolha do ou dos prestadores a quem fosse(m) atribuído(s) os blocos de numeração, seria retomada a metodologia inicial, isto é, o método Query on Release (QoR).

Após os constrangimentos técnicos na implementação do cenário 3, primeiramente invocados por alguns operadores, terem sido ultrapassados, fez-se a análise das vantagens e inconvenientes dos dois cenários. Em síntese, os argumentos dos prestadores mais frequentemente apresentados foram os seguintes:

A favor do cenário 3 - ser uma solução em que cada prestador é autónomo, não existindo custos associados a trabalho e processamento no envio de sinalização para redes de outros operadores;

Contra o cenário 3 - não dar solução para serviços de mensagens (non-call related3) com origem no estrangeiro;

A favor do cenário 4 - dar resposta também no caso de comunicações de mensagens com origem no estrangeiro;

Contra o cenário 4 - ser uma solução que requer um procedimento de reatribuição de blocos, exigindo uma solução transitória na qual os serviços de mensagem (non-call related) não funcionariam e obrigando a diferentes tipos de encargos para os prestadores, incluindo o pagamento de taxas de utilização de números.

Todos os prestadores se manifestaram a favor do cenário 3, à excepção do Grupo PT e da Radiomóvel (embora num cenário de isenção de taxas de utilização dos blocos reatribuídos). A Colt não manifestou preferência, referindo ter condições para se preparar para qualquer dos cenários.

Assim, decidiu-se pelo cenário 3.

No que respeita à insuficiência do cenário 3 para os serviços non-call related foi considerado prematuro, nesta fase, a adopção de uma solução técnica, uma vez que a mesma não está normalizada para chamadas com origem internacional.

Neste contexto, os operadores de serviço telefónico móvel (incluindo um prestador MVNO - ZON) apresentaram um documento com uma proposta de acções a desenvolver para encontrar uma solução para estes serviços que conclui fundamentalmente o seguinte:

Não é possível estabelecer uma Especificação de Interface Técnico que resolva, de um modo pleno, a totalidade das situações de extinção;

No caso da extinção de um dos actuais MNO não se vislumbra uma solução razoável e implementável, devendo por isso merecer uma avaliação dos procedimentos a adoptar de modo a minimizar o impacto para os consumidores e restantes operadores;

Esta situação pode também verificar-se no caso de existir um futuro MNO de menor dimensão ou de um Full MVNO;

No caso de MVNO light, os operadores de suporte a estes prestadores assumirão temporariamente (por prazo não superior a 6 meses) a responsabilidade de encaminhamento deste tipo de comunicações.

Adicionalmente este documento propõe que este assunto seja aprofundado no âmbito de um Grupo de Trabalho com actividade a iniciar em Setembro.

2.1.2 Anexo I

Face ao exposto, a Especificação da Interface técnica entre redes - anexo I - teve as seguintes alterações principais:

Integração no documento publicado no sítio do ICP-ANACOM da solução em uso para os serviços non-call related;

Inserção do cenário que prevê a implementação, para blocos de numeração específicos (de serviços extintos), da metodologia de encaminhamento baseada na solução ACQ ou uma técnica de encaminhamento semelhante, deixando de haver para um determinado bloco de numeração a mensagem de libertação para trás com causa n.º 14 (REL#14);

Inclusão, como Apêndice B à Especificação, do documento dos operadores móveis.

2.2 Análise do Anexo II - Processos Administrativos

As alterações com maior impacto nesta especificação derivam não só da exigência de acomodar a situação de previsão da extinção de serviço por parte de uma empresa, mas também de adequar os temporizadores aos novos prazos e as mensagens e causas de recusa às novas condições em vigor para os pedidos de portabilidade.

Cada um destes aspectos é analisado em separado.

2.2.1 Extinção de serviço

O artigo 12.º do Regulamento alterado previa já um papel para a ER no âmbito da extinção de serviço. Assim, está previsto que, na ausência do prestador que extingue o serviço, a ER, ''em nome'' desse prestador, proceda às funções de prestador detentor/doador (PD), no caso do primeiro pedido de portabilidade efectuado desde a extinção de serviço até 3 meses após essa data (tempo de quarentena), para os números de clientes do serviço extinto.

Neste sentido foi introduzida uma secção descrevendo as funções emuladas pela ER.

Também, o processo de retorno de números requer que se prevejam acções adicionais a desenvolver por parte da ER. A opção pelo cenário 3 no Interface técnico entre redes previu ainda funções de alerta pela ER no fim do processo de retorno iniciado pelo primeiro prestador detentor de um número de blocos atribuídos à empresa com o serviço extinto, para o avisar da devolução do mesmo, ao ICP-ANACOM. Por outro lado, se o cenário escolhido tivesse sido o 4 haveria de proceder de forma massiva a uma alteração de NRN4, neste caso, com impacto directo nos prestadores.

2.2.2 Temporizadores

Uma das principais alterações do Regulamento foi a redução do tempo de antecedência mínimo do pedido de portabilidade face à data agendamento para a portabilidade, permitindo assim um prazo na oferta desta funcionalidade para o utilizador final muito menor do que o actual. Esta redução, de 5 para 2 dias úteis nos números móveis e de 8 também para 2 dias úteis no caso dos outros números, não alterou a forma de contagem dos tempos.

Contudo, o Grupo PT alegou que a forma de contagem dos prazos previstos na Especificação de Portabilidade, em vigor desde 2001, e depois transpostos para o Regulamento n.º 58/2005, não estavam de acordo com o regime de contagem de prazos legal, estipulado no Código Civil, por estarem os mesmos a ser contados em horas úteis quando estão expressos em dias úteis.

O ICP-ANACOM defendeu que os prazos previstos no Regulamento Alterado foram definidos de acordo com os pressupostos que sempre vigoraram na validação pela ER dos pedidos electrónicos de portabilidade e, como tal, deve ser essa a leitura do Regulamento.

Foi, ainda, clarificado que a hora de referência considerada actualmente na validação do pedido electrónico de portabilidade, pela ER, para a janela que constitui a primeira opção no tempo, é o meio da respectiva janela (11:30 horas, 16:30 horas ou 19:30 horas).

Sendo este assunto uma questão maior que ultrapassava o estrito âmbito da especificação, requerendo outro nível de abordagem e procedimento, a contagem ''dia útil'' manteve o pressuposto de ''24 horas seguidas contadas nos dias úteis''.

Um outro temporizador que gerou algum debate foi o temporizador que estabelece a antecedência mínima para o cancelamento de um pedido de portabilidade. Neste caso, o Regulamento não determina nenhum valor específico, apenas definindo os termos em que o cancelamento pode ou deve ser efectuado. Alguns prestadores expressaram preocupação por não poderem acolher uma alteração de vontade do assinante, tendo o ICP-ANACOM referido que é difícil conciliar prazos curtos para a portabilidade com o ''direito ao arrependimento''.

Nesta matéria, o ICP-ANACOM apenas vincou a necessidade de todos os prestadores ficarem ''confortáveis'' com o valor que viesse ser a definido, que entendia dever ser o maior de entre as propostas apresentadas, para evitar falsas portabilidades de números por prestadores que não tinham, em tempo, agido em conformidade com o pedido de cancelamento. O valor acordado entre os prestadores para este temporizador foi de 12 horas.

Por fim, e à margem das alterações determinadas pelo Regulamento, foi duplicado o valor para o temporizador que permite o envio dos diversos pedidos electrónicos que integram um pedido coerente5. Tratou-se de uma proposta do Grupo de Trabalho, em alternativa à proposta inicial do Grupo PT, de maior complexidade, de aceitar pedidos coerentes com mensagens não ordenadas sequencialmente e também bem aceite por aquele grupo empresarial.

2.2.3 Condições para os Pedidos de Portabilidade

Outra alteração muito significativa do Regulamento prende-se com os elementos que devem constar do pedido de portabilidade e, consequentemente, com os motivos para rejeição quando esses elementos faltam ou estão errados. Adicionalmente, a supressão no Regulamento do envio obrigatório de alguns elementos deu origem à extinção de causas de rejeição.

Por outro lado, se a redução no tempo para obter a portabilidade joga sobretudo a favor dos consumidores, a fixação de condições associadas ao pedido que torne fácil a sua automatização, em termos de tratamento informático, é fundamental para alcançar essa redução sem perda de segurança para o consumidor.

Com este entendimento e com o acordo da maioria dos prestadores, deu-se cumprimento ao determinado pelo Regulamento no que se refere à eliminação da obrigação de envio de morada nos pedidos electrónicos de portabilidade de números geográficos e à criação da obrigação de envio de um número de identificação do titular.

Na sequência de uma proposta apresentada pela ZON para a extensão do campo destinado ao nome do titular, em resultado da sua experiência de que 25% dos nomes de clientes ficavam truncados, foram ponderadas vantagens e custos, tendo sido maioritariamente considerado vantajoso aumentar o comprimento do campo destinado ao nome, pese embora, no quadro do novo regulamento, constituir este um elemento supletivo.

Os prestadores acolheram positivamente uma proposta recuperada pelo ICP-ANACOM, apresentada na fase de Consulta Pública ao Regulamento da Portabilidade, onde era sugerido enviar, para implementações do serviço telefónico em local fixo sobre GSM/UMTS e para facilitar a identificação de um assinante, o número do SIM no pedido de portabilidade.

Também no processo de consulta foi identificada a necessidade de ser harmonizado o formato preciso do SIM, número que é obrigatório ser enviado nos pedidos de números móveis. Esta alteração foi consensual e ficou decidido que este campo deveria ser preenchido com identificador completo, na base da recomendação E.1186 da UIT-T (sem check sum) e caso não fosse preenchido completamente o pedido seria rejeitado.

Quanto aos motivos de rejeição a pedidos electrónicos de portabilidade devem assentar na filosofia de existir, para cada motivo, um código de causa de recusa. Ora, por um lado, a especificação da portabilidade foi elaborada anteriormente ao Regulamento n.º 58/2005 da Portabilidade, existindo, por esse motivo, causas de rejeição desajustadas, sendo que, por outro lado, o Regulamento Alterado elimina e cria outras causas de recusa. Embora, por prudência, exista também um código genérico de recusa que, quando usado, requer o preenchimento de um campo de observações para ser indicado qual o problema associado a esse pedido, é factor de agilização e transparência dos processos reduzir ao mínimo a utilização desse código genérico.

Com este entendimento, e com o acordo da maioria dos prestadores, foram eliminadas e criadas várias causas de recusa. Por proposta da Vodafone e com a concordância de todos os outros prestadores, à excepção do Grupo PT, foi ainda desdobrada a causa relacionada com a rejeição devida à Titularidade/Identificação. Foi justificado este desdobramento pelo facto de permitir a clarificação da causa de rejeição - erro no nome ou erro no número do documento de identificação - facilitando assim a correcção do elemento errado no pedido electrónico seguinte para o mesmo número.

Por último, foi aceite uma proposta do Grupo PT para a utilização de campos disponíveis na mensagem de confirmação do pedido de portabilidade e na mensagem de retorno, aquando da simultaneidade de pedidos de portabilidade com retorno de lacete, a fim de facilitar a sincronização dos dois processos.

2.2.4 Outros

O Grupo PT apresentou a sua preocupação no que respeita ao interface de suporte às comunicações entre os prestadores e a ER, por considerar ser insuficiente a actual capacidade. Neste sentido, defendeu que se deveria rever a especificação de processos neste ponto.

O entendimento expresso pela maioria dos presentes (prestadores e ER) foi de que essa capacidade depende do tráfego gerado por cada prestador, sendo a responsabilidade de dimensionamento da ligação de cada um. Estando já isto disposto no respectivo ponto da especificação, entendeu-se que não era necessário efectuar qualquer alteração.

Por último, foi considerado fundamental que, durante a fase de implementação, fossem criadas condições para testar as alterações da especificação de processos. A ER informou já que conta disponibilizar, no ambiente de Desenvolvimento e para testes, a solução de acordo com esta especificação alterada, um mês antes da mesma entrar em vigor.

Embora marginal à alteração do Regulamento, mas por constituir matéria do interesse deste grupo, o ICP-ANACOM fez uma apresentação relativa a uma aplicação suportada nos seus sistemas que constitui uma melhoria importante, em termos de funcionalidades, relativamente à actual Extranet da portabilidade.

2.2.5 Anexo II

Face ao exposto, a Especificação de Processos administrativos para a portabilidade de operador - anexo II - teve as seguintes alterações principais:

Adopção e tradução (do inglês) do documento base com a versão 2.04 da Especificação de Processos Administrativos para a Portabilidade mantida pela ER e disponível na Extranet da portabilidade.

Introdução de uma secção com a especificação das funções a serem desempenhadas pela ER devido à emulação, por esta, de um prestador que extinguiu o serviço (secção 3.10).

Definição de novos valores para os temporizadores:

- T3 (Tempo de resposta máximo para um pedido de portabilidade): 24 horas seguidas contadas em dias úteis - de acordo com o n.º 7 do artigo 12.º do Regulamento;

- T4/T4M (Tempo mínimo até à portabilidade (fixo) / Tempo mínimo até à portabilidade (móvel)): 48 horas seguidas contadas em dias úteis - de acordo com o n.º 5 do artigo 12.º do Regulamento;

- T16 (Tempo limite para envio de NP Return): 2 dias - de acordo com o n.º 1 do artigo 16.º do Regulamento;

- T2 (Tempo máximo para enviar todas as mensagens de um pedido coerente): 60 minutos - para melhorar o processo de envio de pedidos coerentes;

- T9 (Ponto de não retorno de pedido de portabilidade) e

- T13 (Ponto de não retorno de alteração do NRN): 12 horas.

Alterações e adições relativas aos formatos de mensagens ou parâmetros:

- Na mensagem NP Request, a codificação dos parâmetros CustomerStreet, CustomerLocation e CustomerCodeAndLocation, passa de mandatória para opcional;

- Na mensagem NP Request, o estado dos parâmetros CustomerDocumentIDType e CustomerDocumentID, é alterado de opcional para mandatório;

- Na mensagem de NP Request, o estado do parâmetro CustomerSIM é alterada de ''não aplicável à rede fixa'', para ''opcional'';

- Nas mensagens de NP Return e NP Request Confirmation, os parâmetros Auxiliary1, Auxiliary2 e Auxiliary3 são introduzidos e designados para as funções de LocalLoopNumber, LocalLoopCoordinates e LoopHDFTerminationpara identificar o lacete a ser devolvido, sendo os mesmos opcionais. A informação nesses parâmetros é a seguinte:

. Auxiliary1 - Local Loop Number, com comprimento de 10 caracteres;

. Auxiliary2 - Loop HDF Block (Bloco HDF), com comprimento de 2 caracteres;

. Auxiliary3 - Loop HDF Termination (Terminação HDF), com comprimento 3 caracteres;

- Aumento do comprimento do parâmetro CustomerName de 50 caracteres para 80 caracteres;

- Redução do comprimento do parâmetro CustomerSIM de 20 caracteres para 19 caracteres;

- Introdução da codificação ''3=Nómada'' no parâmetro TypeOfNumber;

- Adição das seguintes codificações no parâmetro CustomerIDType:

. 3=Título de Residência;

. 4=Cartão do Cidadão.

Alterações das causas de rejeição:

- Foram eliminadas as seguintes causas de rejeição, tendo sido marcadas como para ''Reservado para uso futuro'':

. Causa 301 (Falta denúncia/alteração do contrato);

. Causa 303 (Morada não corresponde à morada de instalação (só para números geográficos)).

- Foram criadas as seguintes causas de rejeição:

. Causa 311 (Número referente a um Posto Público) - de acordo com a alínea a) do número 2 do artigo 3.º e com a alínea a) do n.º 2 do artigo 13.º do Regulamento;

. Causa 312 (Número referente a um aceso temporário) - de acordo com a alínea b) do número 2 do artigo 3.º e a alínea a) do n.º 2 do artigo 13.º do Regulamento;

. Causa 315 (Excedida a capacidade nas opções indicadas no pedido (a ser eliminada a 1 de Janeiro de 2010)) - de acordo com os números n.ºs 5 e 6 do artigo 13.º do Regulamento;

. Causa 313 (Documento de identificação não corresponde (não aplicável a pré-pagos não identificados)).

- Foi alterada a seguinte causa de rejeição:

. Causa 300 (Titularidade não corresponde (não aplicável a assinaturas pré-pagas não identificadas))

3. Outros assuntos

O Grupo PT apresentou a questão de não ser operacionalmente possível, no caso de uma extinção de serviço em que a empresa não respeite o prazo regulamentarmente definido de pré-aviso aos seus clientes e regulador - mínimo de 15 dias -, assegurar a plena continuidade de serviço aos clientes com números de blocos de numeração atribuídos à empresa com serviço extinto. Neste sentido, o Grupo PT expressou a importância de ser definido um prazo máximo razoável para execução da obrigação de encaminhamento de chamadas para tais números.

O ICP-ANACOM reconheceu o problema de uma extinção sem pré-aviso, mas considerou que o Regulamento não dá margem para definir prazos, pois que se estaria nesse caso a desrespeitar o próprio regulamento, uma vez que é suposto o encaminhamento directo das chamadas para números portados dos blocos do serviço extinto ser efectuado a partir da data da extinção publicitada pelo ICP-ANACOM. Adicionalmente referiu que o que estava em causa era o serviço de cada prestador aos seus clientes e que a continuidade de serviço é requerida genericamente e dentro do que é razoável, pelo que entendia que se tratava de uma questão a montante da própria portabilidade.

4. Deliberação

Assim, no âmbito das atribuições previstas na alínea b) do n.º 1 do artigo 6.º dos Estatutos do ICP-ANACOM, aprovados pelo Decreto-Lei n.º 309/2001, de 7 de Dezembro, e ao abrigo do disposto no n.º2 do artigo 4º do Regulamento n.º 87/2009 do ICP-ANACOM, apresenta-se agora ao Conselho de Administração, para aprovação, a Especificação de Portabilidade alterada.

Notas

nt_title

1 Tempo de Quarentena - período de três meses durante o qual cliente tem direito a utilizar o mesmo número para o mesmo serviço (na mesma ou noutra empresa, pedindo a portabilidade).
2 A indisponibilidade resulta de constrangimentos técnicos actuais que podem não se colocar na altura em que a situação ocorra.
3 Serviços que utilizam apenas a rede de sinalização. Por oposição a serviços Call related, baseados na comutação de canais.
4 NRN - Network Routing Number - número que resulta da concatenação do número portado com o código de encaminhamento da empresa onde o número está ported-in.
5 Pedido coerente - um conjunto de pedidos electrónicos de portabilidade relativos a vários números e ou várias gamas de números do mesmo assinante, tratados como um só e, consequentemente, portados na mesma janela.
6 O formato de acordo com esta recomendação é: ''89351xydddddddddddd''.

Consulte:

Especificação de Portabilidade - Anexo I (Interface técnico entre redes)

(PDF 738 KB)

Especificação de Portabilidade - Anexo II (Processos administrativos para a portabilidade de operador)

(PDF 1212 KB)

## Documentos

- [Especificação de Portabilidade - Anexo I (Interface técnico entre redes)](https://www.anacom.pt/streaming/anexo1_portabilidade13042009.pdf?contentId=914801&field=ATTACHED_FILE)
- [Especificação de Portabilidade - Anexo II (Processos administrativos para a portabilidade de operador)](https://www.anacom.pt/streaming/anexo2_porta13042009.pdf?contentId=914824&field=ATTACHED_FILE)

Fonte: https://www.anacom.pt/render.jsp?contentId=914719
