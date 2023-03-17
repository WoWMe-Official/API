CREATE TABLE `account_types` (
 `ID` tinyint NOT NULL,
 `account_type` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `available_days` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id` int NOT NULL,
 `day` int NOT NULL,
 `start_time` datetime NOT NULL,
 `end_time` datetime NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `challenges` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id` int NOT NULL,
 `name` varchar(255) NOT NULL,
 `background` varchar(255) NOT NULL,
 `profile_picture` varchar(255) NOT NULL,
 `description` text NOT NULL,
 `start_date` int NOT NULL,
 `end_date` int NOT NULL,
 `distance` float NOT NULL,
 `reward` varchar(255) NOT NULL,
 `organization` int NOT NULL,
 `leaderboard` int NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `challenge_details_day` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `day_hash` tinytext NOT NULL,
 `day_id` int NOT NULL,
 `start_time` datetime NOT NULL,
 `end_time` datetime NOT NULL,
 `is_start` tinyint(1) NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `events` (
 `id` int NOT NULL AUTO_INCREMENT,
 `hash` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
 `uuid` int NOT NULL,
 `background_image` tinytext NOT NULL,
 `title` tinytext NOT NULL,
 `description` text NOT NULL,
 `num_excercises` int NOT NULL,
 `difficulty` tinytext NOT NULL,
 PRIMARY KEY (`id`),
 UNIQUE KEY `hash` (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `fitness_goals` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id` int NOT NULL,
 `goal` tinytext NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `fitness_level` (
 `level` int NOT NULL,
 `description` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `genders` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `gender` tinytext NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `leaderboard` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `name` tinytext NOT NULL,
 `pace` int NOT NULL,
 `distance` int NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `organization` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `name` tinytext NOT NULL,
 `image_route` tinytext CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
 `distance` int NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `ratings` (
 `rating_id` bigint NOT NULL AUTO_INCREMENT,
 `rater` int NOT NULL,
 `rated` int NOT NULL,
 `rating` int NOT NULL,
 PRIMARY KEY (`rating_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `registration` (
 `user_id` int NOT NULL AUTO_INCREMENT,
 `email` varchar(320) NOT NULL,
 `password` tinytext NOT NULL,
 `phone` tinytext NOT NULL,
 `first_name` tinytext NOT NULL,
 `last_name` tinytext NOT NULL,
 `birthdate` datetime DEFAULT NULL,
 `about_you` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci,
 `gender` tinyint NOT NULL DEFAULT '0',
 `account_type` int NOT NULL DEFAULT '0',
 `facebook` tinyint DEFAULT '0',
 `instagram` tinyint DEFAULT '0',
 `timestamp_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
 `timestamp_edited` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `relationships` (
 `relationship_id` bigint NOT NULL AUTO_INCREMENT,
 `relationship_type` tinyint NOT NULL,
 `user_id_1` int NOT NULL,
 `user_id_2` int NOT NULL,
 `pending_response` tinyint(1) NOT NULL,
 `target` int NOT NULL,
 PRIMARY KEY (`relationship_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `blocks` (
 `id` bigint NOT NULL AUTO_INCREMENT,
 `blocker_id` int NOT NULL,
 `blocked_id` int NOT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `specializations` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id` int NOT NULL,
 `specialization` tinytext NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `stats` (
 `id` int NOT NULL AUTO_INCREMENT,
 `uuid` int NOT NULL,
 `hash` tinytext NOT NULL,
 `title` varchar(255) NOT NULL,
 `stat` int DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `stat_workout_hash` (
 `id` int NOT NULL AUTO_INCREMENT,
 `uuid` int NOT NULL,
 `stat` tinytext NOT NULL,
 `workout` tinytext NOT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `tokens` (
 `token_id` int NOT NULL AUTO_INCREMENT,
 `token` tinytext NOT NULL,
 `user_id` int NOT NULL,
 `auth_level` int NOT NULL,
 PRIMARY KEY (`token_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `trainer_client_history` (
 `session_id` bigint NOT NULL AUTO_INCREMENT,
 `trainer_id` int NOT NULL,
 `client_id` int NOT NULL,
 `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `trainer_information` (
 `user_id` int NOT NULL,
 `social_security_number` tinytext NOT NULL,
 `identification` tinytext CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci,
 `rate` int NOT NULL,
 `payment_method` tinytext NOT NULL,
 `certification_photo` tinytext CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `trainer_stats` (
 `trainer_id` int NOT NULL,
 `wallet_balance` decimal(10,0) NOT NULL,
 `earnings_total` decimal(10,0) NOT NULL,
 `taxes_total` decimal(10,0) NOT NULL,
 `hours_worked` decimal(10,0) NOT NULL,
 `sessions_worked` int NOT NULL,
 `categories_assigned` int NOT NULL,
 `client_count` int NOT NULL,
 `steps` int NOT NULL,
 `distance` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `user_information` (
 `user_id` int NOT NULL,
 `height_ft_in` decimal(10,0) NOT NULL,
 `weight_lb` int NOT NULL,
 `height_cm` int NOT NULL,
 `weight_kg` int NOT NULL,
 `body_fat_percentage` int NOT NULL,
 `fitness_level` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
CREATE TABLE `workout` (
 `id` int NOT NULL AUTO_INCREMENT,
 `hash` tinytext NOT NULL,
 `uuid` int NOT NULL,
 `workout` varchar(255) NOT NULL,
 `reps` int DEFAULT NULL,
 `weight` float DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `workout_plan` (
 `id` int NOT NULL AUTO_INCREMENT,
 `uuid` int NOT NULL,
 `name` varchar(255) NOT NULL,
 `rating` float DEFAULT NULL,
 `workouts_completed` int DEFAULT NULL,
 `fitness_level` varchar(255) DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
CREATE TABLE `inbox` (
 `inbox_id` int NOT NULL AUTO_INCREMENT,
 `inbox_token` tinytext NOT NULL,
 `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
 `sender` int NOT NULL,
 `subject_line` tinytext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
 `content` text NOT NULL,
 `message_edited` tinyint(1) NOT NULL DEFAULT '0',
 PRIMARY KEY (`inbox_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `bcc` (
 `bcc_id` int NOT NULL AUTO_INCREMENT,
 `inbox_token` tinytext NOT NULL,
 `uuid` int NOT NULL,
 PRIMARY KEY (`bcc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `cc` (
 `cc_id` int NOT NULL AUTO_INCREMENT,
 `inbox_token` tinytext NOT NULL,
 `uuid` int NOT NULL,
 PRIMARY KEY (`cc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `inbox_perms` (
 `id` bigint NOT NULL AUTO_INCREMENT,
 `inbox_token` tinytext NOT NULL,
 `user_id` int NOT NULL,
 `can_access` tinyint(1) NOT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `favorites` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id_1` int NOT NULL,
 `user_id_2` int NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `requests` (
 `request_id` int NOT NULL AUTO_INCREMENT,
 `requesting_user_id` int NOT NULL,
 `requested_user_id` int NOT NULL,
 `request_status` int NOT NULL COMMENT '0 = denied, 1 = pending, 2 = accepted',
 `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY (`request_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `organization_members` (
 `id` int NOT NULL AUTO_INCREMENT,
 `organization_id` int NOT NULL,
 `user_id` int NOT NULL,
 `user_org_admin` tinyint(1) NOT NULL,
 `user_org_owner` tinyint(1) NOT NULL,
 `recruiter` int DEFAULT NULL,
 `request_status` int NOT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `challenge_members` (
 `id` int NOT NULL AUTO_INCREMENT,
 `challenge_id` int NOT NULL,
 `user_id` int NOT NULL,
 `recruiter` int NOT NULL,
 `request_status` int NOT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;