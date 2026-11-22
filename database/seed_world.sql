USE aetheria_mud;

INSERT INTO rooms (id, title, description, exits, ambient) VALUES
(1, 'The Whispering Fen - Sunken Causeway',
 'Rotting wooden planks span dark, stagnant marsh water. Will-o-wisps drift above twisted reeds. A stone archway leads north toward the Guild Sanctuary.',
 '{"north": 3, "east": 2}', 'marsh'),
(2, 'Bog Hollow - Reed Thicket',
 'Thick cattails and knee-deep mire slow every step. Fresh claw marks score the mud.',
 '{"west": 1}', 'marsh'),
(3, 'Aetheria Guild Sanctuary',
 'Torches illuminate weapon racks, arcane training circles, and a Quartermaster counter. Type train to advance ranks or shop to browse gear.',
 '{"south": 1}', 'sanctuary')
ON DUPLICATE KEY UPDATE
 title = VALUES(title),
 description = VALUES(description),
 exits = VALUES(exits),
 ambient = VALUES(ambient);
