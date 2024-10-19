CREATE TABLE `user-role-db`.`tbl_role` (`id` INT NOT NULL AUTO_INCREMENT , `roleName` VARCHAR(32) NOT NULL , `accessModules` VARCHAR(256) NOT NULL , `createdAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `active` TINYINT(1) NOT NULL DEFAULT '1' , PRIMARY KEY (`id`));

CREATE TABLE `user-role-db`.`tbl_user` (`id` INT NOT NULL AUTO_INCREMENT , `role_id` INT NOT NULL , `firstName` VARCHAR(32) NOT NULL , `lastName` VARCHAR(32) , `email` VARCHAR(256) NOT NULL , `password` TEXT NOT NULL , PRIMARY KEY (`id`));
