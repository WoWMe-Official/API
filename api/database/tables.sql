CREATE TABLE `registration` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(320) NOT NULL,
  `password` tinytext NOT NULL,
  `timestamp_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `timestamp_edited` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `tokens` (
  `token_id` int NOT NULL AUTO_INCREMENT,
  `token` tinytext NOT NULL,
  `user_id` int NOT NULL,
  `auth_level` int NOT NULL,
  PRIMARY KEY (`token_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;