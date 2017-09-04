INSERT INTO campaigns (name, description, description_es, created_at, updated_at)
VALUES ('Fullstack Javascript Developer', 'Excellent English. Experience with NodeJS and AWS on backend, while AngularJS or Angular 2 on frontend. 2 or more years of experience.', 'Alto nivel de Inglés. Experiencia en NodeJS y AWS para backend y AngularJS o Angular 2 en frontend. 2 o más años de experiencia.', now(), now());

INSERT INTO campaigns (name, description, description_es, created_at, updated_at)
VALUES ('Systems Administrator', 'Excellent English. Experience with Windows OS, Linux OS and VMware. Know a scripting language. Able to work in a 24/7 environment', 'Alto nivel de Inglés. Experiencia con Windows OS, Linus OS y VMware. Saber por lo menos un lenguaje de scripting. Disponibilidad 24/7', now(), now());

INSERT INTO campaigns (name, description, description_es, created_at, updated_at)
VALUES ('C/C++ Developer', 'Multinational company position with excellent English. C/C++ experience, detailed oriented and good for team work.', 'Vacante en multinacional con alto nivel de Inglés. Experiencia en C/C++, orientado al detalle y capaz de trabajar en equipo', now(), now());

INSERT INTO campaigns (name, description, description_es, created_at, updated_at)
VALUES ('Senior .NET C# developer', 'Multinational company position with excellent English. Senior developer with experience in .NET, C# and Equities related systems, detailed oriented and good for team work.', '', now(), now());


UPDATE campaigns
SET description_es = 'Alto nivel de Inglés. Experiencia en NodeJS y AWS para backend y AngularJS o Angular 2 en frontend. 2 o más años de experiencia.'
WHERE id = 1;

UPDATE campaigns
SET description_es = 'Alto nivel de Inglés. Experiencia con Windows OS, Linus OS y VMware. Saber por lo menos un lenguaje de scripting. Disponibilidad 24/7.'
WHERE id = 2;

UPDATE campaigns
SET description_es = 'Vacante en multinacional con alto nivel de Inglés. Experiencia en C/C++, orientado al detalle y capaz de trabajar en equipo.'
WHERE id = 3;


# The remote ubuntu machine does not support accents therefore I opted for a remote connection sending the correct spanish syntax:
# follow this structure: ssh_commands psql.... \" SQL....\'string\' \".
# note that SQL command cannot have ";" at the end.
ssh -i production_key.pem <user>@<host> psql -d maindb -U dbadmin -p 5432 -h localhost -c \" UPDATE campaigns SET description_es = \'Alto nivel de Inglés. Experiencia en NodeJS y AWS para backend y AngularJS o Angular 2 en frontend. 2 o más años de experiencia.\' WHERE id = 1 \"

ssh -i production_key.pem <user>@<host> psql -d maindb -U dbadmin -p 5432 -h localhost -c \" UPDATE campaigns SET description_es = \'Alto nivel de Inglés. Experiencia con Windows OS, Linus OS y VMware. Saber por lo menos un lenguaje de scripting. Disponibilidad 24/7.\' WHERE id = 2 \"

ssh -i production_key.pem <user>@<host> psql -d maindb -U dbadmin -p 5432 -h localhost -c \" UPDATE campaigns SET description_es = \'Vacante en multinacional con alto nivel de Inglés. Experiencia en C/C++, orientado al detalle y capaz de trabajar en equipo.\' WHERE id = 3 \"

ssh -i production_key.pem <user>@<host> psql -d maindb -U dbadmin -p 5432 -h localhost -c \" UPDATE campaigns SET description = \'Vacante en multinacional con alto nivel de Inglés. Senior developer con experiencia en .NET, C# y sistemas relacionados con acciones, orientado al detalle y capaz de trabajar en equipo.\' WHERE id = 4 \"

ssh -i production_key.pem <user>@<host> psql -d maindb -U dbadmin -p 5432 -h localhost -c \" UPDATE campaigns SET description_es = \'Vacante en multinacional con alto nivel de Inglés. Senior developer con experiencia en .NET, C# y sistemas relacionados con acciones, orientado al detalle y capaz de trabajar en equipo.\' WHERE id = 4 \"
