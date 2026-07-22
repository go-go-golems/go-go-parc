# Branch · Fenêtre de contexte IA

- URL: https://chatgpt.com/c/6a60d467-ea54-83ea-a6f1-c291e3b06277
- Created: 2026-07-22T14:32:40.073Z

---

> Microphone  •  00:00
> Merci. 
>
> Unknown  •  00:27
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  00:32
> Merci. 
>
> Unknown  •  00:57
> Sous-titrage Société Radio-Canada Sous-titrage Société Radio-Canada 
>
> Microphone  •  01:36
> ... ... 
>
> Unknown  •  01:57
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  02:01
> ... ... 
>
> Unknown  •  02:27
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  02:52
> ... 
>
> Unknown  •  02:57
> Sous-titrage Société Radio-Canada Sous-titrage Société Radio-Canada ... ... 
>
> Speaker 1  •  03:38
> ... 
>
> Microphone  •  03:41
> Hello. Hello. Yeah, good afternoon from Montpellier, same as you, I suppose. ok but you're on the same time zone right 
>
> Speaker 1  •  03:56
> ... 
>
> Microphone  •  04:12
> ok ok yeah ok I will just yeah I will just introduce myself et puis donner le mic à Manuel O'Donald qui est ici avec nous. Manuel est de l'US mais est un ingénieur de l'AI français-german. Je vais le laisser vous l'introduire. Je suis Pierre Vanier, je suis le CEO de Flint. Je suis aussi un ingénieur de software. Flint est une entreprise de consultation et spécifiquement MPTC, pour les 8 derniers ans. 
>
> Speaker 1  •  04:55
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  04:55
> Et nous avons compté environ 10 ou 12 contracteurs qui travaillent sur le site à Montpellier. Et je connais Adrien et Yann depuis 4 ans. Et j'ai entendu de vous, Nigel, 
>
> Speaker 1  •  05:11
> Oh wow, que grève! 
>
> Microphone  •  05:11
> mais je ne vous ai jamais rencontré. En bonne manière, 
>
> Speaker 1  •  05:14
> Oh wow! 
>
> Microphone  •  05:14
> bien sûr. 
>
> Speaker 1  •  05:16
> Yeah, yeah, now I'm impressed! 
>
> Microphone  •  05:19
> Et nous sommes ici pour parler et peut-être répondre à vos questions sur un nouveau service que nous proposons, qui est de aider les développeurs et les ingénieurs de la software à regagner la contrôle sur leurs consommations de tokens et à réduire leurs coûts, etc. Donc, je donne la parole à Manuel pour sa présentation. 
>
> Speaker 2  •  05:41
> Before you start, maybe, Emmanuel, 
>
> Microphone  •  05:42
> Oui. 
>
> Speaker 2  •  05:43
> is that okay if I record? 
>
> Microphone  •  05:45
> Oui, bien sûr. 
>
> Speaker 2  •  05:45
> Greg est un peu tard et Vasilis, je ne sais pas si il va nous rejoindre ou non. 
>
> Microphone  •  05:50
> yep 
>
> Speaker 2  •  05:50
> Est-ce que ça va? Ok. 
>
> Speaker 3  •  05:56
> Je m'appelle Manuel, j'ai rencontré Pierre à une conférence d'AI il y a deux ans, un an et demi. J'ai été développeur toute ma vie, donc mon focus était toujours de construire de la software de qualité, de la shipping, et quand les outils d'AI ont commencé à appearing I think about four years ago now with copilot alpha those kinds of 
>
> Microphone  •  06:16
> ... 
>
> Speaker 3  •  06:16
> tools I I was like this is a fantastic tool to just do better engineering all around so since then I've been extensively working with it to ship products to build a lot and yeah I'm seeing the world now catching up and it's a my techniques are grounded in four years of experience now so it's C'est un bon début, il me semble. C'est tout Pierre, j'ai oublié quelque chose? 
>
> Microphone  •  06:43
> Oui, non, non, non, nous avons, oui, nous avons, comme, désolé. 
>
> Speaker 1  •  06:45
> Tu es en mute. On ne peut pas lire sur ta main, mais ça va. 
>
> Microphone  •  06:50
> Oui, oui, nous, quand nous avons rencontré Manuel deux ans auparavant, nous nous sommes rencontrés à New York et à San Francisco. 
>
> Speaker 1  •  06:52
> Merci. 
>
> Microphone  •  06:58
> Il était un parlementaire pour cette conférence d'ingénierie AI. Et on a réussi à faire ça et on a décidé qu'il était un peu en manque et le travail offert pour les professionnels ingénieurs de software pour utiliser ces nouvelles outils qui changent drastiquement la façon dont ils travaillent et leur travail est destiné. Et nous avons décidé de créer deux offres différentes. Une est un workshop, un type de curriculum de formation régulier. Et il y a un autre sujet qui est le sujet de ce meeting aujourd'hui, qui est un "meet-up". Je suppose que tout le monde qui est autour de la table ici connaît un "meet-up". 
>
> Speaker 1  •  07:49
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  07:54
> Je ne vais pas mentionner, mais j'ai co-créé un groupe de "meet-up" à Montpellier, qui s'appelle "Gen AI Meet-up Group" à Montpellier. Et, malgré le fait que la ville est assez petite en France, c'est la 7e ville la plus grande en France, on a 1400 membres et on rencontre régulièrement, presque chaque mois, 
>
> Speaker 1  •  08:19
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  08:20
> avec plus de 100 personnes. 
>
> Speaker 1  •  08:22
> ... 
>
> Microphone  •  08:22
> Donc, on sait comment gérer ces communications et ces rencontres. Mais ce que nous parlons de ce meet-up est un meet-up privé, en site, SLB, custom. Et nous sommes prêts à peut-être répondre à vos questions parce que vous avez des questions, Yann. Mais aussi, peut-être que Nigel peut se présenter parce que je connais Adrien, je connais Yann, mais je ne connais pas Nigel sur son scope. 
>
> Speaker 4  •  08:50
> sure 
>
> Microphone  •  08:50
> et oui. 
>
> Speaker 4  •  08:53
> yeah so my name is Nigel Leicester I've been with the company 30 plus years I started off in development and have then moved into software and practices so three years I've had all sorts of different sort of jobs so developer project manager etc nowadays I focus a lot principally on governance, so software governance of the 
>
> Microphone  •  09:20
> Merci. 
>
> Speaker 4  •  09:22
> tools, but I've looked after, but I also managed all of our products, like Azure DevOps, etc., a whole suite of tools for the company. But my current focus now is on all things AI as well. That's another key theme at the moment, and so hence, very interested in what you've got to say on AI. So that So we're interested in things like the adoption, the impact, the rollout, tooling that we're using, techniques and practices, etc. So and this seems to be talking about token maximizing or token minimizing even. 
>
> Microphone  •  10:03
> Yeah. 
>
> Speaker 4  •  10:08
> So I'm based in Abingdon, the UK. So that's just south of Oxford. uh it's in the middle towards the bottom of uh of you of the uk okay 
>
> Speaker 1  •  10:30
> abadino there there's a big gap between those two 
>
> Speaker 4  •  10:36
> yeah yeah likewise 
>
> Speaker 2  •  10:43
> Je pense que le but de ce meeting est d'avoir assez d'insights 
>
> Microphone  •  10:50
> ... 
>
> Speaker 2  •  10:53
> pour pouvoir prendre une décision éducative en quelques minutes. C'est ce que nous avons besoin. Évidemment, nous aurons des questions, mais je pense que pour la completité, et peut-être pour Nigel aussi, ce serait bien si vous aviez une introduction sur ce que le Masterclass ou le Meetup est. avec des questions sur les objectifs et la façon dont vous voulez structurer le projet. 
>
> Speaker 5  •  11:19
> Et puis, je pense qu'Adrien a quelques questions aussi. On peut les prendre en suivant, ou à la fin, selon ce que vous présentez. Merci. 
>
> Microphone  •  11:50
> mais je suis très confiant et je suis beaucoup plus là. Je serai le seul à être sur site. Donc, l'idée est de créer un meet-up. 
>
> Speaker 5  •  11:59
> Merci. 
>
> Microphone  •  12:01
> Nous avons déjà run ce meet-up pour Club Med, qui est une autre grande entreprise en France, mais plus petite que SLB, et non pas multinationale comme SLB, et non pas industrielle. On a organisé ce meet-up en site à Paris dans leur facility Club Med. Il y avait 60 ingénieurs de développement de software, de génial à senior. 
>
> Speaker 1  •  12:29
> Je pense qu'il y en a 60 à l'adresse en 4D. 
>
> Microphone  •  12:34
> 60 en site et 40 en remote. Donc, il y avait environ 100 ingénieurs de software. Et l'idée principale est que les ingénieurs de software ne se rappellent pas de tout ce qu'ils ne feront pas. Ils n'ont pas les mains sur les choses. Si ils regardent des slides, si ils écoutent quelqu'un qui récite un cours ou qui regarde un MOOC ou autre, ils ne vont pas se rappeler du cœur de l'expertise et des techniques, etc. 
>
> Speaker 1  •  12:59
> Merci. 
>
> Microphone  •  13:13
> So we decided with Manuel to have a very hands-on meet-up. That is to say, we are not working, although Manuel is doing a lot of demo, but the engineers and the software engineers on site, they're working. Usually, we want to couple them as twins, like pair programming, two of them, 
>
> Speaker 1  •  13:31
> Merci. 
>
> Microphone  •  13:38
> because it enhances the communication between the software engineers while they're doing their hands-on and their exercises. And maybe, Manuel, you can give a more focus about the very core of the meet-up in terms of what is a subject and why we choose this very subject in the first place. Merci. 
>
> Speaker 3  •  14:29
> language models and they're probabilistic and there's the core concept as a context window which is what we use to convey a lot of these engineering skills that will improve 
>
> Microphone  •  14:38
> ... 
>
> Speaker 3  •  14:44
> basically every developer in the company and reduce token costs for example once you have an understanding of what actually a token is and how you can leverage them and we do that by a series of increasingly bigger scoped exercises. It doesn't matter which tool, which model you use, because at the end of the day, they're all kind of the same anyway. So, we just 
>
> Microphone  •  15:10
> ... 
>
> Speaker 3  •  15:13
> say like, you can open chatgpt.com if you want. And the goal is really, because it is skill that is mostly I think gained by practice and not by hearing about it to have these like to encourage these exchanges between developers because I think that's like a big issue especially in team context where 
>
> Microphone  •  15:33
> Merci. 
>
> Speaker 3  •  15:36
> people still focus on the code as the artifact to be reviewed to be to be to be shared but code review for example being more about the exchange of knowledge than necessarily improving the quality of the code. I know it's a little bit controversial but that's like my take. We encourage this kind of conversation from the beginning which will improve people to share how they prompt, why they chose something, what worked, what didn't to encourage this kind of practical knowledge gain. Pierre, does that cover? 
>
> Microphone  •  16:09
> Et oui, je veux ajouter quelque chose. On a décidé de créer un rendez-vous pour être agnostique en termens de la tâche que vous utilisez. 
>
> Speaker 3  •  16:19
> Merci. 
>
> Microphone  •  16:19
> Parce que ce que nous appelons les harnesses, ce sont ces gros software équipés avec différents outils et prévents systèmes et ce que les vendeurs veulent mettre dedans, et qu'ils sont subjectés à des changements très rapidement. Et ce que nous voulons que les engineers de la software comprennent est la core de la façon dont ça fonctionne, ce qui est possible avec ça, Et comment vous pouvez leverger ce savoir fondamental. Mais ne me faites pas mal rire, on ne passe pas beaucoup de temps sur les slides. Je pense que le plus gros slide est juste un slide sur les LLM, qui couvre l'attention, le concept d'attention, le concept d'autoregressive, et le concept d'autoregressive. 
>
> Speaker 3  •  17:13
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  17:15
> Et bien sûr, la partie centrale est la fenêtre contexte. 
>
> Speaker 3  •  17:15
> Merci. 
>
> Microphone  •  17:18
> Parce que nous avons remarqué que les ingénieurs de software ne comprennent pas du tout notre travail de fenêtre contexte. Et c'est comme le travail de l'ingénieur de software. Ils doivent être en mesure de savoir ce qui est dans leur fenêtre contextuelle et d'optimiser ça en avant pour pouvoir avoir... Comme la plupart des LLM, ils peuvent presque tout en un coup si vous avez une documentation technique très bonne et des stratégies de prompting. et une très profonde compréhension de votre contexte que nous faisons comme ingénieurs de software. Et nous ne voulons pas que ce meet-up soit juste... Oui. 
>
> Speaker 3  •  18:15
> basically, d'être là pour mettre des choses intéressantes dans ce contexte et ensuite obtenir un résultat. Mais c est pour ça que nous le faisons comme un point central. Une fois que vous comprenez ça, vous pouvez changer d'agent, vous pouvez changer de clé, vous savez les compétences ou les outils, ou vous pouvez tout éviter de ce débat assez facilement. Et les techniques de prompting que j'utilise sont les mêmes que j'utilisais 3 ans auparavant, 
>
> Microphone  •  18:37
> ... 
>
> Speaker 3  •  18:39
> où, réellemment, la planète de l'esprit était comme... Les modèles ne peuvent pas écrire un seul fonctionnement à l'époque. 
>
> Microphone  •  18:56
> Oui, c'est vrai. On ne veut pas que ce meet-up soit une tendance qui devient tout à fait old-fashioned la semaine prochaine. On veut que les ingénieurs de software changent leur manière de penser. Et l'idée est que les tokens et la consommation d'AI ne sont pas ouvertes pour tout le monde. C'est comme si ça allait si vite avec cette agence de software engineering et même les ingénieurs de software n'ont pas eu assez de temps pour comprendre la fonction et la fonction de la core et comment optimiser votre travail. Par exemple, 40 ans auparavant, on optimisait pour les mémoires 
>
> Speaker 3  •  19:42
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  19:44
> parce que les mémoires étaient petites. On optimisait pour la computation par les CPU et des choses comme ça. On devrait revenir à un plus frugal et un plus sauvé de tokens minimisés, comme vous le disiez, Nigel, pour pouvoir réduire votre invoix ou ce qu'il y a, ou au moins contacter ce type de stratégie de maximum de tokens de YOLO. 
>
> Speaker 3  •  20:12
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  20:13
> Et regrouper la contrôle sur votre propre craft et le cœur de votre devoir comme ingénieur de software To be an engineer and not to be a validator of what AI decides you to do. 
>
> Speaker 1  •  20:22
> Merci. 
>
> Microphone  •  20:27
> Vous devez être en train de créer votre fenêtre de contexte et de savoir très profondément quelles outils sont utilisés, comment votre agent et votre loop agentique fonctionnent, comment votre honnêteté fonctionne. Et cette rencontre est à ce sujet. Oui, Manuel. Oui. 
>
> Speaker 2  •  21:15
> si les travaux de la société que vous supportez 
>
> Microphone  •  21:16
> Merci. 
>
> Speaker 2  •  21:20
> a l'improvisé ou au moins a la même qualité avec un coût moins bas, parce que nous avons un peu de difficulté avec Nigel, et nous avons un équipement dédié pour définir les matriques, pour comprendre l'impact de l'AI, et il est déjà difficile de trouver les matriques correctes pour mesurer ça, Et si on commence à changer la façon dont les gens travaillent, il est idéal que vous ayez un système de mesure en place avant de vous entraîner pour voir le second impact, par exemple. Je me demandais si vous couvrez ce genre de choses pendant la classe. 
>
> Microphone  •  22:02
> Manuel est moins de start. 
>
> Speaker 3  •  22:05
> Les métriques de productivité de la software ont toujours été un sujet compliqué, je pense, surtout dans les grandes entreprises. Il y a un métier qui est maintenant éminemment trackable. 
>
> Microphone  •  22:16
> Merci. 
>
> Speaker 3  •  22:17
> C'est le produit. Le résultat du team change pendant que les coûts de token diminuent. C'est un métier très bien que nous pouvons avoir. Personnellement, mon métier personnel, pour voir si ça marche, c'est de voir comment beaucoup d'ingénieurs commencent à s'investir en programmation. Il y a une tendance, après 20 ans de travail, 30 years on the job to be a little bit blasé. What I keep seeing after my workshops is that these people are suddenly building 
>
> Microphone  •  22:46
> ... 
>
> Speaker 3  •  22:47
> tons of projects on their own time, really invested in improving legacy code bases. In terms of metrics, I wonder if you have metrics in place to do this. 
>
> Speaker 2  •  23:00
> They are being discussed at the moment. We have identified 10 metrics so far. Obviously, we would be able to share them with you si vous êtes intéressés, où on va regarder le temps cycle. Donc, on tente de regarder les métriques traditionnelles, car ce sont probablement les métrique que vous pouvez mesurer 
>
> Microphone  •  23:19
> ... 
>
> Speaker 2  •  23:21
> avant l'introduction de l'AI et c'est là que vous allez probablement voir des trends ou non. Donc, ce sont les 3 choses. Et puis, on a aussi ajouté des métriques spécifiques de l 'AI qui sont données par les outils qu'ils ont, comme le curseur, qui vous donne des insights qui peuvent évaluer le type de prompts, par exemple, que vous utilisez quand vous jouez avec Cursor. Mais il serait bien de recevoir des feedbacks d'extérieur aussi sur ça. 
>
> Microphone  •  23:46
> ... 
>
> Speaker 2  •  23:50
> Et ma seconde question est sur l'exercice, parce que vous avez dit que vous voulez que les classes soient agnostiques, 
>
> Microphone  •  24:15
> Manuel, I give you the mic. The metric. And the other question about the tool they're using. et... yeah. 
>
> Speaker 2  •  24:57
> on a mis les métriques en place, donc on ne les a pas encore rapportés. On est encore en train de les discrét 
>
> Microphone  •  25:15
> ... 
>
> Speaker 3  •  25:27
> et ma focus a toujours été sur la qualité. Si le software est bon, vous aurez ces effets downstream qui sont difficiles à mesurer parce que les choses ont été faites tout à l'avant. Ce sont plus à la hauteur du niveau de l'output de l'équipe, je pense. 
>
> Microphone  •  25:47
> Merci. 
>
> Speaker 3  •  25:47
> Quelle est la qualité des projets délivrés? Est-ce qu'ils sont en fait faits en temps? traditional metrics that I would look at in terms of those improvements. And in terms of the tools, because the tools are so similar, like it's a text box that you type stuff in and then it writes files that hopefully are good files. Having workflows like sharing prompts or building up a common set of tools, that's something that we definitely approach. 
>
> Microphone  •  26:19
> ... 
>
> Speaker 3  •  26:19
> Like we, As we were discussing the changes we would like to have for SLB, 
>
> Microphone  •  26:25
> ... 
>
> Speaker 3  •  26:25
> which is a much more distributed company than Club Med, instead of focusing just on fundamentals and inter-team dynamics, we want to add a couple of exercises or a section about 
>
> Microphone  •  26:40
> ... 
>
> Speaker 3  •  26:41
> how do you build tools that allow increased effectivity of using AI. Mais si c'est Cursor, Cloud ou XYZ, si ils ont le même MCP ou le même command line tool, ils vont bénéficier de l'un et de l'autre. Au final, ils sont les mêmes tools. Est-ce que ça répond à votre question? 
>
> Speaker 2  •  27:03
> Oui et non. Non, parce que pour l'exercice, je suppose, ils vont nécessiter des outils à utiliser. So, does that mean that everybody is free to choose the tools they want? 
>
> Speaker 3  •  27:20
> Yeah. 
>
> Speaker 1  •  27:22
> Oh. 
>
> Speaker 3  •  27:23
> Yeah, that's... 
>
> Speaker 1  •  27:29
> Okay. 
>
> Speaker 3  •  27:34
> Most exercises, you can do literally in chatgpt.com or, you know, like, whatever. 
>
> Microphone  •  27:37
> Merci. 
>
> Speaker 3  •  27:40
> Mais certains exercices qui sont plus liés au code et qui utilisent des outils comme Command Line sont mieux faits sur votre propre computer. Mais en ce qui concerne l'outil, nous encourage les gens à utiliser ce qu'ils font tous les jours pour utiliser comme exemple, si ils peuvent, leur base de code quotidienne. Parce que sinon, les choses seront un peu contrives. Si vous voyez ces techniques fonctionner sur ce que vous faites tous les jours, 
>
> Speaker 2  •  28:05
> be much more easy to communicate I think. - So that means that we will not be using skills for example, as you post, to add some context if we use 
>
> Microphone  •  28:13
> ... 
>
> Speaker 3  •  28:17
> chatgpt type of tools. - That's where the concept of context, when it comes in, if you paste a file into chatgpt.com, that's kind of exactly the same as a skill in some way right? And explaining that will help people to like, I do most 
>
> Microphone  •  28:30
> Merci. 
>
> Speaker 3  •  28:34
> de mes actuales en chat GPT calm juste because I prefer the interface but it doesn't really make a difference in terms of I understand there's going to be some context in here for chat GPT calm I have to paste it or I have to say you know look on the web or so if I'm in cloud code I can maybe skip that and say like the skill has been pre-installed it's been shared across the team I don't need to worry about it and and I think it's this understanding that is that est le clé pour gérer le changement de landscape. Il y a de nouveaux outils et de nouveaux modèles. Chaque deux mois, il va y avoir une relance, il va y avoir du hype partout. Si vous comprenez les bases, vous allez vous dire "ok, c'est juste le même" et vous vous concentrez sur le fait de le leverager. Je pense que c'est clair, mais je pense que Yann a un point de vue, il y a probablement 
>
> Speaker 6  •  29:26
> some subtility tool after tool, right? What you just said, Manuel, right? Some tools you may have to skip this, some tools 
>
> Microphone  •  29:30
> Merci. 
>
> Speaker 6  •  29:32
> you may be able to do this and this easily. So, probably the question is, can we have a small part of it showing how to optimize the usage of the tool we have, right? That's what I see. 
>
> Speaker 3  •  29:43
> That's the section we wanted to add. And we will use skills, because those are actually a pretty good, a pretty well shared standard to do this, like add files to the context. And then for tooling, cli tooling is usually the perfect solution right it's like it's completely agnostic mcp 
>
> Microphone  •  30:00
> Merci. 
>
> Speaker 3  •  30:05
> so just like more complicated to put in place and often don't add that much value so the focus is going to be just on cli tools because i assume so that's actually a good question how many developers use windows because that's something i really don't know how coding agents 
>
> Microphone  •  30:30
> Merci. 
>
> Speaker 3  •  30:52
> different techniques, I don't think it's really conducive to 
>
> Microphone  •  31:00
> ... 
>
> Speaker 3  •  31:01
> actually tell them to use a different tool. The technology being so you know it's kind of a mirror of what you put in in some ways. In many ways if you're comfortable with what you put in, you will be comfortable with what comes out. 
>
> Speaker 6  •  31:15
> Just to answer your question, we were thinking with Yan à un point, de ne pas mettre que les développeurs. Juste pour revenir à ce que tu as dit, je pense que c'est là où peut-être il y aura une subtilité et probablement un niveau différent d'entendu, parce que nous pouvons mettre 
>
> Microphone  •  31:29
> Merci. 
>
> Speaker 6  •  31:32
> le portfolio avec eux aussi. Juste pour qu'ils comprennent qu'ils ne devraient pas faire tout sur leur propre et consommer tous les ressources qu'on a pour essayer de construire quelque chose, mais plus de travail avec les développeurs et s'assurer que nous avons un bon esprit team aussi, même avec les nouveaux outils. new techniques, not new tools, like you said. 
>
> Speaker 3  •  31:54
> Pierre, you want me to answer? Or Nigel first. 
>
> Speaker 4  •  32:01
> Yeah, we've got access to four GPT tools at the box, of which two, everyone should have access to, and two, they have to be on boarded for licensing reasons. So, they have, so, you know, that's Claude and Cursor. And then we got a couple of flavors of GPT. So, and the GPT ones, look, you know, they're just copilot or whatever. 
>
> Microphone  •  32:29
> Merci. 
>
> Speaker 4  •  32:32
> They're just, looks to be a simple interface. And there may be some controls on the back end for memories and prompts and system type edits. But anyway, so there's a choice of things there. Yeah, I was going to ask about the scope. Was it developers only? Mais si c'est des développeurs, en théorie, ils sont les uns qui ont déjà utilisé les outils, donc ils auront accès, donc ça devrait être bien. Est-ce que c'est un one-off ou un multi... un one-off session, ou est-ce une série de sessions sur un set de semaines? Parce que un meet-up est comme un soir, répété une fois par mois ou quelque chose comme ça. Qu'est-ce que c'est que le format? 
>
> Microphone  •  33:29
> C'est, c'est, so, we want to do it, or maybe we, we could do it at MPTC with, with, with whatever, how, I don't know how, how many engineers that you can have and, on site and, and maybe other people from other centres or, or remote personnel or whatever. So, and we, and we assume we should have a batch of about 100 people. We've not tried with more than that. et c'est un événement qui ne veut pas dire qu'on ne peut pas organiser d'autres types 
>
> Speaker 4  •  34:10
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  34:10
> d'événements comme les workshops que je parlais, qui sont plus craftés et customisés pour les teams plus petits. Ce qui peut être, par exemple, intéressant, ce que nous avons vu avec d'autres clients, c'est qu'ils construisent ce qu'on appelle une guilde 
>
> Speaker 4  •  34:41
> Sous-titrage Société Radio-Canada Sous-titrage Société Radio-Canada 
>
> Speaker 1  •  35:22
> Merci. 
>
> Microphone  •  35:28
> Mais ça peut aussi être un obstacle ou quelque chose de plus difficile pour avoir un vrai succès. On sait qu'on va avoir un vrai succès pour les ingénieurs de software. Et peut-être d'autres types de personnes comme UI, UX, portfolios, QA, 
>
> Speaker 1  •  35:43
> Merci. 
>
> Microphone  •  35:47
> et les managers, si vous pensez à ça, ou peut-être les managers de top, parce qu'ils doivent savoir comment gérer et leverager l'AI. Et si vous mixez trop de types de personnes, Through the same meet-up, you risk something that is to disappoint like maybe everybody because you try to a one-side fits all. For everyone, and not everyone, it's just one-side fits all. Manu, if it does make sense what is said. C'est prêt. Merci. 
>
> Speaker 3  •  36:43
> mais je pense que ça fonctionne dans un groupe plus petit. Et aussi, dans le contexte d'une grande entreprise comme SLB, ça fait plus sens dans des projets très focus, qui ont été très heureux de vous entendre, vous en avez beaucoup, et des hackathons. Donc, nous avons fait, en fait, beaucoup de workshops pour essayer de trouver les pairs les plus hétérogènes de personnes qui collaborent ensemble, Because that's where not only the most interesting outcomes happen, but also this collaboration is often something that's like missing in standard team structures, where the real unlock of AI happens, right? It's like... 
>
> Speaker 4  •  37:28
> So from a cost perspective, definitely we want to target the software developers parce qu'ils sont les seuls à encourer les coûts de token d'increment à large scale relative aux autres parties de l'organisation. Donc, la chose d'autre, c'est que les gens ont une compréhension générale de comment ces choses fonctionnent, c'est une bonne chose. oh le point est juste comme from a mind oh elle come back to some in it now come back in the same sadly d'a I can't help with that 
>
> Speaker 3  •  38:11
> yeah and another thing yes there's a cross 
>
> Microphone  •  38:13
> Merci. 
>
> Speaker 3  •  38:19
> yeah yeah I mean taking notes in workshops in sorry in calls is like a big component 
>
> Microphone  •  38:43
> Merci. Merci. 
>
> Speaker 3  •  39:25
> prompting techniques that would be hard to communicate with all developers, right, like things that go into compiler techniques and much more targeted, advanced, you know, how do we build tooling to ensure software quality for the company, requires a certain type of developer 
>
> Microphone  •  39:43
> Merci. 
>
> Speaker 3  •  39:45
> that, in that context, I think, would be lost. So, yeah, the 100-person meetup is really like focused on base engineering based cost reduction at the larger scale and then a strategic impact which you know probably will take a bit of time to get or it could happen really quickly is this more like smaller team where people debrief like see what the other pairs are doing as well I know 
>
> Speaker 4  •  40:12
> what my follow-on point was now it is that there are two use cases there's optimizing token usage within software development as in the the actual act 
>
> Microphone  •  40:17
> Merci. 
>
> Speaker 4  •  40:21
> de développer des softwares, mais nous avons aussi construit des outils ou des produits pour les personnes qui utilisent des LLM ou des AIs. Et donc, il y a aussi un gestionnement, il y a aussi un gestionnement de ces choses. Les techniques, en théorie, certaines sont très portables entre tout cela, mais je 
>
> Microphone  •  40:43
> ... Je voulais juste vous dire, je pense qu'il y a aussi un très grand périmètre et un domaine qui peut être tackled avec une meilleure compréhension et une meilleure utilisation de ces techniques sont les SRE, les DevOps et tous ces gens qui sont souvent oublis et qui sont en département. mais vous pouvez vraiment leverager les outils 
>
> Speaker 4  •  41:43
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  41:44
> et l'automatisme, l'automatique, le déploiement, le CICD, etc. Je me souviens, avec Manuel, on a déclenché un déploiement très compliqué sur les multipod avec Kubernetes, etc. Et tout ça avec le prompt correct, juste un coup, tout le déploiement, c'était vraiment fou. 
>
> Speaker 3  •  42:06
> Pierre, 
>
> Microphone  •  42:06
> Je pense que vous avez... Oui. 
>
> Speaker 3  •  42:07
> Pierre, let me just, Nigel, just to make sure I understood your question, you were talking about like both using AI for development et puis sur l'autre côté, on construit des produits avec des... 
>
> Microphone  •  42:19
> Yeah. 
>
> Speaker 4  •  42:19
> Oui, c'est vraiment, vraiment, vraiment, c'est vraiment le code, le fait de passer par le code, etc. etc. et de construire des choses, mais il y a aussi ce que nous construisons, donc ça va avoir, vous savez, nous allons utiliser euh, nous allons utiliser des systèmes basés sur l'AI, des systèmes basés sur la génétique, etc. dans ces outils, donc maintenant, je suppose que beaucoup de concepts sont fortement portables, donc... 
>
> Microphone  •  42:39
> Merci. 
>
> Speaker 3  •  42:43
> Je dois dire que je n'ai pas fait beaucoup de produits qui ont l'AI dans le loop. Je pense que normalement ils ne l'ont pas besoin. Je veux dire, c'est controversé, mais je pense qu'il y a beaucoup de choses que je peux montrer en termes d''idées sur comment vous pouvez faire ça, qui basé sur le fait que l'outil peut écrire des codes, So it should write code to present ad hoc UI interfaces or so. 
>
> Microphone  •  43:09
> Merci. 
>
> Speaker 3  •  43:15
> After that, in terms of concrete building with LLMs, I see an LLM as just like a very slow, very expensive HTTP call. So you get back to distributed systems, which have a complexity that hasn't really been seen before, is that these providers have like the worst uptime of any service I've ever seen. Et donc, ici, pour juste dire, pour aller en arrière, c'est principalement un problème de système distribué. C'est un problème assez dur, 
>
> Microphone  •  43:47
> ... 
>
> Speaker 3  •  43:47
> parce que vous avez ces contraintes difficiles, ces coûts hauts, pour montrer que la meilleure solution pour approche de ces, c'est d'utiliser l'AI pour construire des outils pour vous aider à construire ou à gérer ces nouveaux... nouveaux défis en termes de... en termes d'applications d'API, d'accord? Et un agent va juste faire des applications d'API dans un loop, si vous voulez les paralyser, quels patterns sont les meilleurs pour les applications face à un client, je ne suis pas vraiment un expert sur ça. Mais le contexte-window-understanding va bien sûr se transférer un à un. 
>
> Speaker 2  •  44:22
> Et ça, c'est probablement pas le focus de la classe, je suppose. 
>
> Microphone  •  44:26
> Non. 
>
> Speaker 2  •  44:26
> Je veux dire, pour EnsoNagia, je pense que le premier cas d'utilisation 
>
> Speaker 1  •  44:30
> c'est ce que nous nous concentrons sur. Ok, ce qui signifie que le code... 
>
> Microphone  •  44:33
> Mais ça va définitivement les aider à comprendre le cœur. 
>
> Speaker 1  •  44:35
> Merci. 
>
> Microphone  •  44:38
> Parce que Context Window est important, en cas où vous l'utilisez comme un outil pour l'amélioration de votre développement ou si vous l'utilisez en product or service, vous aussi vous avez besoin d'entendre tout ça. Donc, ça ne va pas être perdu. Mais c'est un paradigme différent et c'est un workshop différent ou pour pouvoir construire et injecter les fonctionnalités de l'LM et de l'AI 
>
> Speaker 1  •  45:05
> ... 
>
> Microphone  •  45:06
> dans le bon endroit, dans le bon sens. Peut-être que vous avez des problématiques évaluées, qui sont très importantes, comme les non-déterministes. Et je sais que vos géologistes et vos gens ne vous aiment pas les résultats non-déterministes, c'est plutôt comme les déterministes, comme les blancs et les blancs, etc. Je vais essayer. 
>
> Speaker 3  •  45:56
> et vraiment augmenter la route d'itération, 
>
> Microphone  •  45:58
> Merci. 
>
> Speaker 3  •  45:59
> qui est, depuis que j'ai toujours été très proche de les gens avec qui je travaille dans la logistique et l'e-commerce, le réel déclin de l'LLM, quand ils sont sortis, j'ai dû faire beaucoup d'accounts, et puis, dans une session, je pouvais peut-être écrire une enquête SQL et puis mon cerveau explotait, et on ne pouvait que communiquer à un niveau très haut, et je me situe, les enquêtes SQL sont retournées, et ils me disent : "Non, c'est faux." Now, you can write 100 queries in a meeting, 
>
> Microphone  •  46:30
> ... 
>
> Speaker 3  •  46:31
> which will allow the geologist to actually, because they're using cloud code, could get an understanding of what AI actually enables them to do, to then figure out how to best put it into the tool, if that makes sense, I think. 
>
> Microphone  •  46:50
> Hum. 
>
> Speaker 3  •  46:51
> But in terms of... 
>
> Speaker 4  •  46:52
> What it clarifies is that it's definitely the software developers sort of primary focus here as opposed to other cohorts or other other element or other bits of software development so you know like the product development 
>
> Speaker 3  •  47:08
> yeah can I I would like to rephrase that and say that the focus is development development yeah yeah because it has been democratized in a certain way right so being able to spread that but I think that's you know 
>
> Microphone  •  47:20
> Merci. ... 
>
> Speaker 1  •  48:22
> les prompts que j'ai mis dans les démos par exemple. 
>
> Microphone  •  48:24
> Je veux juste ajouter quelque chose. On a développé une plateforme web spécifique que vous allez pouvoir accéder seulement pour SLB. C'est un type de aide pédagogique. C'est une plateforme où vous pouvez trouver all the slides, all the hands out, all the examples, the exercises, the demos. But the core feature is something that you can upload your session, whatever session you have, like maybe Claude Codd or Chris or whatever, and you can literally deep dive into your session and actually realize that when you just prompt what is the time in Houston right now, you will understand that your 20 tokens just generate maybe 20k tokens behind the hood 
>
> Speaker 1  •  49:20
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  49:24
> because your arm has decided to add thinking or because it decided to reveal your whole code base by opening file. And so that gives you a very deep understanding of what your context window is made of and how your different works on it, degrés, ou optimisé, et comment les tokens sont littéralement, vous savez, en volant très rapidement 
>
> Speaker 1  •  49:50
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  49:52
> et ça aide à vraiment comprendre les termes, les "go back and forth", les "tool calls", la pensée avec la pensée de token, etc. 
>
> Speaker 1  •  49:58
> Ok. 
>
> Microphone  •  50:01
> Donc, vous aurez une plateforme. 
>
> Speaker 1  •  50:03
> Je suppose, on ne va pas pouvoir 
>
> Microphone  •  50:05
> Merci. 
>
> Speaker 1  •  50:05
> mettre des données confidentielles là-bas. 
>
> Speaker 3  •  50:10
> Je voulais adresser cela. Bien sûr, nous allons, en termes de contexte de la workshop, les sessions qui seront uploadées qui vont être gardés à cette réconciliation de code. setup and then delete it but the tools are also open source um which is an interesting concept these days which uh allows people within the company to to basically you know just point 
>
> Microphone  •  50:35
> Merci. 
>
> Speaker 3  •  50:37
> your agent at this code base and say can you make the same for us but internally if you find use in these uh in these context visualization or expanding them to be like we're going to share these contacts these these contacts uh these transcripts within the team to et d'en faire partie pour partager cette conna 
>
> Microphone  •  51:05
> ... 
>
> Speaker 3  •  51:24
> non ip sensitive stuff or at least not upload those way you're not or at least 
>
> Speaker 4  •  51:31
> yeah so they probably just need a reminder about that so just just another thing where do you so in terms of product development where do you in the way that the life of the developer and development is changing how do you 
>
> Microphone  •  51:51
> Be my guest. Merci. 
>
> Speaker 3  •  52:14
> parce que tu sais, tu s'en sers tous les prototypes en entre. Je pense que c'est le plus important à déclencher. Après ça, il y a juste un increase en qualité et en être capable de monitor et de faire une assurance de qualité sur les produits de release que tu as. Ce sont souvent des choses qui tombent par le côté, où SRE est comme en utilisant ses propres petits dashboards et puis le software dit "on est sorti". En fait, ce sont des loop de feedback qui bénéficient de la qualité du tout. Donc, être capable de montrer un dashboard est comme deux promptes de plus. Tu veux benchmarker ton outil, tu veux le fuser, tu veux faire tous ces types de QA, tu veux avoir des simulateURs, tu veut avoir quelque chose qui génère des données géologiques statistiquement relevantes 
>
> Microphone  •  53:05
> Merci. 
>
> Speaker 3  •  53:06
> based on a crazy base and model that your geologist gives you, yeah, sure, that's not something you 
>
> Microphone  •  53:35
> Merci. 
>
> Speaker 3  •  53:36
> easy to see is like if someone wants an iPhone app, they'll get an iPhone app tomorrow. And there's no metrics for that, I think. It's just really redefining what DSDLC is. And I think that's an incredibly exciting time to be in, et que personne n'a vraiment découvert. Mais j'ai construit, jusqu'à maintenant, je ne compte pas les choses comme des projets. Je les comptais comme des codes, et je me suis dit : "Ce n'est pas bon, je vais les compter comme des projets." Et maintenant, je me concentre sur les fonctionnalités et les résultats. Pierre. ... 
>
> Microphone  •  54:35
> on veut se concentrer sur la préparation, la mise en place, la documentation et le partage de connaissances. Et peut-être que les ingénieurs de software vont éventuellement devenir des ingénieurs de connaissances, et des créateurs de contexte. On doit créer l'univers en termes de signes, de symboles qui sont les plus optimaux, pour que l'LNM puisse juste se mettre très très vite into what you have in mind. And if you do this work very, very thoroughly, very seriously as a team, and I'm not talking about changing all your workflows. You're a very big company, you have very complex workflows and SDLC and whatever. We're not talking about that. 
>
> Speaker 3  •  55:22
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  55:23
> We're talking about leveraging the maximum of software engineer into understanding that we don't really, on n'est pas très intéressé à la code review parce que nous allons être les meilleurs à préparer le set de outils, de connaissances, de documentation, de transcripts, de tout qui fait le plus sens pour atteindre le futur, le bug, le but, l'objectif de la manière la plus rapide 
>
> Speaker 3  •  55:52
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  55:53
> et la plus sûre sans donner de qualité, comme Manuel a dit. So, I think it's mostly that. 
>
> Speaker 1  •  56:01
> So, do you focus in the… so, because one of the tricks to, you know, token efficiency 
>
> Speaker 4  •  56:08
> is going to be asking the right questions. So, the intent-driven development methodology, or whatever you'd like, we'd like to call it going forward, do you sort of touch base on those sort of things, or is it more the mechanics of how the thing works and if you can understand the mechanics of what it's doing then you can shape your inputs to be so she get the answer 
>
> Microphone  •  56:29
> Merci. 
>
> Speaker 4  •  56:35
> you're hoping to get and not something else 
>
> Speaker 3  •  56:38
> hey I think for this first meetup format it's going to be more about the mechanics and just yeah I'm in general because on the main can't just yeah and asking every developer to like reconsider their role in dsdl see is c'est peut-être un peu trop dans le premier workshop. Mais je pense que pour exemple, ces guildes AI, comme le qu'on a chez Club Med, ce sont les personnes qui s'investissent vraiment dans ce travail et qui se demandent comment ça redéfinit les choses. 
>
> Microphone  •  57:06
> ... 
>
> Speaker 3  •  57:07
> Personnellement, je ne suis plus chez un ordinateur. Je me suis réalisé que, après 30 ans, je n''aime pas vraiment être chez un ordinateure et typer des codes dans un petit bouton. So, my own personal change in terms of my SDLC, mostly working on smaller teams or by myself, is that I will have an idea for a product or for a feature that we discussed, 
>
> Microphone  •  57:29
> Merci. 
>
> Speaker 3  •  57:30
> or just an experiment that I want to do. We'll put it into the prompt, into the agent, say, look for documentation, look for existing code, look for stuff online, resources, and write me a really nice textbook for an intern. est mon prompt. Je suis un intern, je ne sais rien, explique tout à moi. Et puis, je le mets littéralement sur mon tablette et je vais à la café-chauffe, à une table différente, et je l'écris pour deux heures. Donc, le code 
>
> Microphone  •  57:59
> Merci. 
>
> Speaker 3  •  58:01
> est comme un tree en forêt, et maintenant, je suis capable de vraiment se concentrer sur le forêt, faire ces décisions de plus large. Et l''existent structure est je pense c'est pourquoi mon focus a toujours été sur la qualité ça vous permet de s'adopter lentement à ces techniques sans disrupter le plus grand scope de comment vous travaillez maintenant c'est facile de faire ça, d'augmenter la vitesse de durée si vous ne construisez que des dashboards qui ne vont pas être shipés à la production 
>
> Microphone  •  58:31
> Merci. 
>
> Speaker 3  •  58:33
> et je vais partager un lien à ce premier talk que j'ai fait ce premier workshop que j'ai fait deux ans ago à AI Engineering which is this whole thing compressed in one hour. And it's interesting because this was ChatGPT 4.0 at the time. But it starts with, because they're language models and language is what humans use to communicate, really they're not artificial intelligence, they're artificial communication. 
>
> Microphone  •  58:59
> Merci. 
>
> Speaker 3  •  59:01
> And so it makes sense to consider what communication looks like in a collaborative setting to then find out where does AI actually make sense. And often it's not writing the code by itself, right? It's like, that's something we know how to do. It kind of never has been the bottleneck per se. But it seems like maybe the tickets that come from QA are badly formatted. So why not make a tool to format those tickets correctly? Because we never had time before, but now we can make a really nice one. 
>
> Microphone  •  59:32
> Merci. 
>
> Speaker 3  •  59:33
> And maybe that's all you do with the AI, 
>
> Microphone  •  59:59
> ... 
>
> Speaker 2  •  01:00:06
> Est-ce que nous avons assez d'insights pour prendre notre décision, probablement la semaine prochaine, comme je l'ai dit? Adrien, si vous avez d'autres questions sur votre côté, ou Nigel? 
>
> Speaker 1  •  01:00:15
> Autrement, Pierre ou Emmanuel, est-ce que vous avez des questions pour nous? Non, pas de questions sur mon côté, mais nous pouvons discuter de tout ça ensemble. 
>
> Microphone  •  01:00:21
> Je voulais juste peut-être ajouter quelque chose. 
>
> Speaker 1  •  01:00:23
> Merci. 
>
> Microphone  •  01:00:25
> Pour nous, il sera très intéressant de travailler avec vous comme un premier step, peut-être comme un premier meet-up sur le site mobile que je connais, que les gens que je connais, et peut-être expander plus tard. L'idée est de vraiment obtenir un succès. Et ce que nous aimerions, comme métrique, ou des discussions à la main de l'autre, ou des types de équipes différentes, ce sera le meilleur métier, à mon avis. 
>
> Speaker 1  •  01:01:21
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  01:01:24
> Et c'est ce que nous voulons avec Manuel. Parce que nous avons vu des ingénieurs qui étaient très négatifs, très reléctants de l'LLM, et ils ont eu ce moment où ils se sont dit « Ok, je peux travailler mieux avec ça. » je peux garder la partie de la codification parce que j'aime mais je peux l'utiliser pour mieux discuter avec mon portfolio 
>
> Speaker 1  •  01:01:51
> Sous-titrage Société Radio-Canada 
>
> Microphone  •  01:01:53
> mieux discuter avec d'autres équipes donc tout le monde a quelque chose à trouver pour mieux comprendre ces outils et si les gens sont moins productifs plus, oui, c'est ce qu'ils veulent Merci. Merci. 
>
> Speaker 6  •  01:02:53
> Si vous ne m'entendez pas, laissez-moi savoir. Mais ce que nous devons vérifier aussi est si nous voulons inclure notre contracteur ou non. Cela va changer le nombre, mais c'est quelque chose que nous devons vérifier sur notre côté. Parce que, évidemment, nous payons pour leur 
>
> Microphone  •  01:03:06
> Merci. 
>
> Speaker 6  •  01:03:08
> Cursor et cloud subscription, ce qui signifie que c'est aussi bénéfique pour nous si ils rejoignent ce type de rencontre et réduisent le coût de cette réforme. 
>
> Speaker 3  •  01:03:18
> Une chose que nous avons fait quand nous avions les équipes plus petites, 
>
> Microphone  •  01:03:36
> ... 
>
> Speaker 3  •  01:03:51
> Pierre est capable de connaître ces personnes, d'avoir les personnes en personne, ça va, je pense, aider beaucoup comme premier pas. Pierre, peut-être que nous pouvons envoyer le vidéo of this first workshop and then maybe a couple of slides or handouts just to to give a sense of what this looks like sounds good 
>
> Speaker 1  •  01:04:29
> yeah okay and I will try to come back to you next week yeah perfect yeah next time thank you all right great great to me 
>
> Microphone  •  01:04:38
> Merci, Nigel, Yann. Au revoir. bye bye 
>
> Speaker 1  •  01:04:42
> thank you bye bye Sous-titrage ST' 501 
>
> Microphone  •  01:05:25
> Ouais, c'était bien. Moi, j'ai trouvé que c'était bien, je pense. Ouais, ouais, je pense. T'as été bon, en tout cas. Je veux te dire que t'as été bon. Tu vois, je sais te dire quand tu coupes trop la parole, mais t'as été particulièrement clair et t'as pas coupé la parole. et je trouve qu'on s'est bien démerdé. Ouais, j'imagine. 
>
> Speaker 7  •  01:05:46
> et que de temps à autre, et justement dans le contexte professionnel, il faut que tu coupes la parole aux gens. 
>
> Microphone  •  01:05:56
> Oui, bien sûr. 
>
> Speaker 7  •  01:05:56
> Les gens qui avancent, ils gueulent en fait. Et du coup, moi je ne sais jamais quand gueuler parce qu'en fait, 
>
> Microphone  •  01:06:01
> Ben oui. 
>
> Speaker 7  •  01:06:01
> je pourrais le faire tout le temps. 
>
> Microphone  •  01:06:03
> C'est pas facile de savoir quand couper la parole, justement. 
>
> Speaker 7  •  01:06:07
> Ou alors de balancer des trucs dans les bases de code sans rien demander à qui que ce soit. 
>
> Microphone  •  01:06:10
> ouais c'est comme couper la parole mais avec du code ça 
>
> Speaker 7  •  01:06:11
> C'est aussi comme ça que les gens avancent en fait. Et du coup, c'est vraiment très très dur par moi et c'est dur de communiquer aussi le fait que ça fait 40 ans que j'ai ce problème-là et que je me suis tellement adapté, tu vois, que dans ce concept… 
>
> ---
>
> liste des points saillants de ce call dans le cadre de ce meetup

## Synthèse des points saillants du call SLB — Meetup « Context Window Engineering »

### 1. Positionnement général du meetup

Le meetup est présenté comme un **événement privé, sur site et personnalisé pour SLB**, destiné principalement aux personnes qui développent du logiciel avec des outils d’IA générative.

L’objectif n’est pas de former les participants à un outil précis, mais de leur transmettre des compétences durables :

- comprendre le fonctionnement réel des modèles et des agents ;
- reprendre le contrôle sur leur consommation de tokens ;
- mieux construire et gérer leurs fenêtres de contexte ;
- améliorer la qualité des résultats sans dépendre des évolutions rapides des fournisseurs ;
- rester des ingénieurs responsables plutôt que de simples validateurs du code produit par l’IA.

La formulation centrale qui ressort du call est :

> L’ingénieur ne doit pas seulement écrire ou valider du code. Il doit savoir construire, réduire, vérifier et renouveler le contexte donné à l’IA.

---

## 2. Le sujet central : la fenêtre de contexte

Pierre et Manuel ont insisté sur le fait que la **fenêtre de contexte** constitue le cœur pédagogique du meetup.

Les développeurs doivent comprendre :

- ce qui entre réellement dans le contexte ;
- comment les fichiers, règles, historiques de conversation et appels d’outils le remplissent ;
- pourquoi une demande apparemment simple peut générer des milliers de tokens ;
- comment le contexte se dégrade au fil d’une session ;
- comment distinguer le signal utile du bruit ;
- quand continuer une session et quand repartir avec une fenêtre propre ;
- comment documenter correctement un objectif pour permettre à un modèle de produire un résultat pertinent rapidement.

Le meetup doit permettre de comprendre que les différents mécanismes — skills, fichiers joints, règles, mémoire, MCP, outils CLI — sont principalement différentes manières de **mettre de l’information à disposition du modèle**.

---

## 3. Une approche agnostique vis-à-vis des outils

Le contenu doit rester indépendant de Cursor, Claude Code, ChatGPT, Copilot ou de tout autre produit.

La justification donnée est double :

- les outils évoluent très rapidement ;
- leurs principes fondamentaux sont similaires.

Les participants seraient encouragés à utiliser les outils qu’ils emploient déjà dans leur travail quotidien.

Les exercices les plus simples pourraient être réalisés dans une interface conversationnelle. Les exercices portant directement sur une base de code seraient plus adaptés à un agent de code ou à un outil en ligne de commande.

Une section spécifique doit néanmoins être ajoutée pour SLB afin de montrer comment optimiser l’usage des outils disponibles dans l’entreprise, notamment :

- Claude ;
- Cursor ;
- les différentes déclinaisons de GPT ou Copilot ;
- les skills ;
- les outils CLI ;
- éventuellement les MCP, lorsqu’ils apportent une valeur réelle.

---

## 4. Un format fortement pratique

Le meetup ne doit pas être une conférence longue ou un cours magistral.

Le principe est de faire travailler les participants sur une série d’exercices de difficulté et de périmètre croissants.

Le format recommandé comprend :

- très peu de slides ;
- quelques explications sur les LLM, l’attention, l’autoregression et les tokens ;
- des démonstrations courtes ;
- des exercices pratiques ;
- du travail en binômes ;
- des moments de débrief et de partage entre participants.

Le travail en binômes est considéré comme essentiel, car il pousse les développeurs à verbaliser :

- leur intention ;
- leurs prompts ;
- leurs choix de contexte ;
- ce qui a fonctionné ;
- ce qui a échoué ;
- les différences entre leurs approches.

L’objectif est aussi de faire évoluer la culture de partage : ne plus seulement partager du code, mais également les raisonnements, les prompts, les procédures et les contextes ayant permis de l’obtenir.

---

## 5. Retour d’expérience Club Med

Le meetup a déjà été organisé pour Club Med.

Les chiffres mentionnés pendant le call étaient approximativement :

- une soixantaine de participants sur place ;
- une quarantaine à distance ;
- environ cent participants au total.

Le retour d’expérience sert de preuve que le format peut fonctionner à grande échelle, mais le dispositif SLB devrait être adapté à une organisation :

- plus internationale ;
- plus distribuée ;
- plus industrielle ;
- disposant de pratiques et de contraintes de gouvernance plus fortes.

Pierre serait le seul intervenant physiquement sur place. Manuel participerait à distance, notamment pour les démonstrations et les séquences techniques.

---

## 6. Public cible : priorité au développement logiciel

La discussion a permis de clarifier que le public prioritaire est constitué des personnes impliquées dans le développement :

- développeurs ;
- software engineers ;
- potentiellement SRE et DevOps ;
- QA et profils techniques proches du cycle de développement ;
- éventuellement certains contractants.

Nigel a souligné que les développeurs sont probablement les principaux générateurs de coûts de tokens à grande échelle.

Pierre a toutefois insisté sur le fait que les SRE et DevOps peuvent eux aussi fortement bénéficier des agents pour :

- le déploiement ;
- le CI/CD ;
- Kubernetes ;
- l’automatisation ;
- le diagnostic ;
- la production de scripts et d’outils internes.

L’inclusion d’autres profils — produit, portfolio, UX ou management — reste possible, mais présente un risque : rendre le contenu trop général et décevoir tout le monde.

La conclusion implicite est de privilégier un public relativement homogène pour cette première session, puis de créer ultérieurement d’autres formats adaptés à des publics différents.

---

## 7. Taille et nature de l’événement

Le meetup est conçu comme un **événement ponctuel**, et non comme une série de cours hebdomadaires.

La taille envisagée est d’environ cent personnes, même si le nombre réel dépendra :

- des participants disponibles sur le site ;
- de l’éventuelle présence de personnes d’autres centres ;
- de la participation à distance ;
- de l’intégration ou non des contractants.

Pierre a suggéré de commencer par le site MPTC, qu’il connaît déjà, afin d’obtenir un premier succès mesurable avant une éventuelle extension à d’autres entités de SLB.

---

## 8. Mesure de l’impact et métriques

SLB travaille actuellement à la définition d’un ensemble d’environ dix métriques permettant d’évaluer l’impact de l’IA.

Les métriques évoquées comprennent :

- le cycle time ;
- les métriques traditionnelles de livraison logicielle ;
- la qualité des projets livrés ;
- le respect des délais ;
- les données d’usage fournies par Cursor ou d’autres outils ;
- les types de prompts employés ;
- la consommation et le coût des tokens.

La difficulté reconnue par tous est que la productivité logicielle est historiquement difficile à mesurer.

Manuel propose de regarder prioritairement :

- les résultats obtenus au niveau de l’équipe ;
- la qualité des logiciels livrés ;
- l’évolution du coût en tokens ;
- l’amélioration des boucles de feedback ;
- la capacité à tester, simuler, monitorer et documenter davantage ;
- l’engagement renouvelé des développeurs.

Un signal qualitatif important serait de voir des développeurs initialement sceptiques commencer à expérimenter, construire des projets et intervenir plus volontiers sur des bases de code existantes.

SLB a proposé de partager ses métriques en cours de définition afin d’obtenir un regard extérieur de Pierre et Manuel.

---

## 9. Plateforme pédagogique et visualisation des sessions

Pierre a présenté une plateforme web dédiée qui serait mise à disposition de SLB.

Cette plateforme regrouperait :

- les slides ;
- les handouts ;
- les exercices ;
- les exemples ;
- les démonstrations ;
- des outils permettant d’analyser une session d’agent.

La fonctionnalité différenciante consiste à charger la trace d’une session afin de visualiser :

- la composition du contexte ;
- les tokens visibles et invisibles ;
- les appels d’outils ;
- les fichiers ouverts ;
- les allers-retours entre le modèle et les outils ;
- les éventuels tokens de raisonnement ;
- la manière dont la session grossit ou se dégrade.

L’exemple donné est qu’une demande de quelques mots peut entraîner des dizaines de milliers de tokens si l’agent décide d’explorer une base de code ou d’utiliser plusieurs outils.

---

## 10. Confidentialité et sécurité

SLB a immédiatement soulevé la question de l’envoi de données confidentielles vers la plateforme.

Les réponses apportées étaient les suivantes :

- les participants devront être explicitement avertis de ne pas charger de données sensibles ;
- les exemples et exercices pourront utiliser des données non confidentielles ;
- les sessions pourraient être supprimées après l’analyse ;
- l’outil serait open source ;
- SLB pourrait éventuellement le déployer en interne ou reconstruire une version conforme à ses contraintes.

Ce sujet devra être formalisé plus précisément dans la proposition, car la réponse donnée à l’oral est restée un peu hésitante et constitue probablement un point de vigilance important pour SLB.

---

## 11. Ce qui n’entre pas directement dans le périmètre

La discussion a distingué deux sujets :

1. utiliser l’IA pour développer du logiciel ;
2. construire des produits dont l’IA ou les LLM font partie du fonctionnement en production.

Le meetup porte principalement sur le premier sujet.

La conception de produits intégrant des LLM soulève d’autres problématiques :

- non-déterminisme ;
- fiabilité des fournisseurs ;
- latence ;
- coûts ;
- résilience ;
- disponibilité ;
- architecture de systèmes distribués ;
- évaluation des réponses ;
- sécurité et observabilité.

La compréhension de la fenêtre de contexte reste utile pour ces produits, mais leur conception nécessiterait un atelier distinct.

---

## 12. Évolution du métier de développeur

Une partie importante de l’échange a porté sur la transformation du métier.

Plusieurs idées fortes ont émergé :

- le code n’est plus nécessairement l’unité principale de travail ;
- il devient possible de raisonner en fonctionnalités, produits ou résultats ;
- la préparation et la documentation prennent davantage d’importance ;
- les ingénieurs pourraient devenir des « knowledge engineers » ou des « context creators » ;
- le travail consiste de plus en plus à créer un univers de documents, règles, contraintes et symboles compréhensibles par l’agent ;
- la vitesse d’itération augmente fortement ;
- des activités auparavant négligées — tests, simulateurs, monitoring, dashboards, documentation — deviennent moins coûteuses à réaliser.

Manuel a également proposé une vision de l’IA comme une technologie d’**artificial communication** davantage que comme une intelligence autonome : sa valeur se situe souvent dans l’amélioration de la communication entre humains, équipes, métiers et systèmes.

---

## 13. Intent-driven development : présent mais pas central

Nigel a demandé si le meetup abordait les méthodologies de développement pilotées par l’intention, notamment la capacité à poser les bonnes questions et à formuler correctement les objectifs.

Manuel a répondu que la première session resterait plutôt centrée sur :

- la mécanique ;
- les modèles ;
- le contexte ;
- les tokens ;
- les pratiques fondamentales.

La redéfinition complète du SDLC ou du rôle du développeur serait probablement trop ambitieuse pour ce premier meetup.

Ces sujets pourraient ensuite être approfondis dans :

- une guilde IA ;
- des ateliers avancés ;
- de petites équipes ;
- des projets ciblés ;
- des hackathons.

---

## 14. Points de convergence obtenus pendant le call

À la fin de la réunion, plusieurs éléments semblaient compris et acceptés par SLB :

- le meetup est prioritairement orienté développement ;
- il s’agit d’une session ponctuelle et pratique ;
- le format peut accueillir environ cent personnes ;
- les participants peuvent utiliser différents outils ;
- le contenu doit rester indépendant des fournisseurs ;
- les fondamentaux portent sur les tokens et la fenêtre de contexte ;
- une section adaptée aux outils de SLB est attendue ;
- les contractants pourraient être inclus ;
- la confidentialité de la plateforme doit être encadrée ;
- les métriques devront être discutées plus précisément ;
- une première expérimentation sur un site connu est préférable à un déploiement immédiatement global.

---

## 15. Objections et interrogations exprimées par SLB

Les principales questions de SLB ont été :

1. **Comment mesurer l’effet réel du meetup ?**
2. **Le contenu sera-t-il adapté aux outils internes ?**
3. **Quels outils seront nécessaires pour les exercices ?**
4. **Le public doit-il être limité aux développeurs ?**
5. **Le format est-il ponctuel ou récurrent ?**
6. **Les contractants peuvent-ils participer ?**
7. **Les données confidentielles peuvent-elles être chargées sur la plateforme ?**
8. **Le meetup traite-t-il aussi de la construction de produits intégrant des LLM ?**
9. **Aborde-t-il les transformations méthodologiques du SDLC ?**
10. **Comment adapter le format à une entreprise distribuée comme SLB ?**

---

## 16. Prochaines étapes convenues ou suggérées

Pierre et Manuel doivent envoyer :

- la vidéo d’un précédent workshop ou talk ;
- quelques slides ;
- des handouts ;
- des exemples permettant de comprendre concrètement le format.

SLB doit :

- poursuivre la discussion interne ;
- décider si les contractants seront inclus ;
- préciser le nombre de participants ;
- clarifier la composition du public ;
- partager éventuellement les métriques identifiées ;
- revenir avec une décision ou un retour la semaine suivante.

---

## 17. Points à renforcer dans la prochaine proposition

Pour transformer ce call en proposition convaincante, il serait utile de préciser davantage :

- le déroulé horaire exact ;
- les objectifs pédagogiques mesurables ;
- les prérequis techniques ;
- les exercices obligatoires et optionnels ;
- les outils supportés chez SLB ;
- la configuration Windows éventuelle ;
- les règles de confidentialité ;
- le lieu de stockage des sessions ;
- leur durée de conservation ;
- la possibilité d’un déploiement interne de la plateforme ;
- la distinction entre participants sur site et à distance ;
- la contribution exacte de Manuel à distance ;
- les métriques avant/après ;
- le nombre recommandé de participants ;
- le dispositif d’animation pour cent personnes ;
- le rôle des contractants ;
- le livrable remis après l’événement ;
- les suites possibles : guilde, atelier avancé, hackathon ou accompagnement d’équipes.

## Conclusion

Le call a globalement validé l’intérêt de SLB pour un meetup pratique consacré à la maîtrise des agents de développement, des tokens et des fenêtres de contexte.

Le besoin exprimé par SLB n’est toutefois pas uniquement pédagogique. L’entreprise cherche aussi à comprendre comment ce format pourrait contribuer à :

- réduire ses coûts ;
- améliorer ses pratiques ;
- accompagner l’adoption des outils ;
- mesurer leur impact ;
- maintenir sa gouvernance ;
- diffuser des méthodes communes dans une organisation distribuée.

La proposition finale devra donc associer un **socle pédagogique universel** à une **adaptation explicite au contexte, aux outils, à la sécurité et aux métriques de SLB**.


---

> no, list of points that can be used as teasers for the workshop for the developers

## Developer Teasers for the Workshop

- **Where did your tokens actually go?** Inspect what your coding agent added behind the scenes.
- **A 10-word prompt can trigger 20,000 tokens.** Learn why—and how to prevent it.
- **Your context window is your new working memory.** Learn how to control what enters, stays, and gets removed.
- **Better prompts are not necessarily longer prompts.** Provide the right information, not more information.
- **Know when to continue a session—and when to start fresh.**
- **Stop making the model rediscover your codebase on every task.**
- **Turn documentation, conventions, and examples into reusable AI context.**
- **Understand the hidden cost of tool calls, file reads, reasoning, and agent loops.**
- **Use skills, rules, files, CLI tools, and MCPs without becoming dependent on one vendor.**
- **Compare how two developers solve the same task with different contexts.**
- **Diagnose why an agent produced the wrong code instead of simply prompting it again.**
- **Reduce token consumption without sacrificing software quality.**
- **Move from “AI-generated code review” to reviewing the intent, context, and constraints.**
- **Use AI on your real engineering work—not artificial tutorial exercises.**
- **Build context that lets an agent solve a task correctly in one pass.**
- **Share more than code: share prompts, decisions, failed approaches, and working context.**
- **Apply the same techniques across Cursor, Claude, ChatGPT, Copilot, and future tools.**
- **Remain the engineer—not the validator of whatever the agent generates.**


---

> topics, not clickbait

- Context windows: structure, limits, and lifecycle  
- Tokens: what they are and where they are consumed  
- Prompt construction for software engineering tasks  
- Managing relevant and irrelevant context  
- Session hygiene: when to continue, summarize, or restart  
- File selection and codebase scoping  
- Tool calls, agent loops, and hidden token usage  
- Skills, rules, memory, CLI tools, and MCPs  
- Tool-agnostic workflows across Cursor, Claude, ChatGPT, and Copilot  
- Preparing technical documentation for AI-assisted development  
- Reusable team context and shared prompting practices  
- Pair exercises using real development scenarios  
- Debugging poor or inconsistent model outputs  
- Reducing token consumption while maintaining quality  
- Reviewing intent, assumptions, and context—not only generated code  
- Using AI for testing, refactoring, documentation, and maintenance  
- Applying AI in DevOps, SRE, CI/CD, and automation workflows  
- Security and confidentiality when sharing code and sessions  
- Measuring AI usage, cost, quality, and delivery impact  
- The evolving role of developers in AI-assisted software engineering


---

> yeah, now condense that into 3-4 points and then we can work on a teaser mail
>
> Think hard beforehand to turn this into a clear message

- **Understand how coding agents work:** context windows, token consumption, tool calls, agent loops, and session lifecycle.  
- **Build better context:** scope files effectively, structure prompts, manage sessions, and reuse documentation, rules, skills, and tools.  
- **Apply the techniques to real engineering work:** coding, debugging, testing, refactoring, maintenance, DevOps, and automation—independently of the AI tool used.  
- **Improve team-level outcomes:** maintain quality and security, share effective practices, reduce unnecessary token usage, and evaluate impact.

