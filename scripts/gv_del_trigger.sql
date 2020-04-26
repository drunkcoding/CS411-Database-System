CREATE DEFINER=`root`@`localhost` TRIGGER `antientropy_cs411`.`gunviolence_gunviolence_BEFORE_DELETE` BEFORE DELETE ON `gunviolence_gunviolence` FOR EACH ROW
BEGIN
	DELETE FROM `gunviolence_gun` WHERE incident_id = OLD.id;
    DELETE FROM `gunviolence_participant` WHERE incident_id = OLD.id;
END