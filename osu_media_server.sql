-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- 생성 시간: 24-05-08 16:18
-- 서버 버전: 10.4.28-MariaDB
-- PHP 버전: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 데이터베이스: `osu_media_server`
--

-- --------------------------------------------------------

--
-- 테이블 구조 `beatmapsinfo`
--

CREATE TABLE `beatmapsinfo` (
  `id` int(11) NOT NULL,
  `osu_file_format_v` tinytext DEFAULT NULL,
  `first_bid` int(11) DEFAULT NULL,
  `BeatmapID` int(11) DEFAULT NULL,
  `BeatmapSetID` int(11) DEFAULT NULL,
  `BeatmapMD5` char(32) DEFAULT NULL,
  `file_name` text DEFAULT NULL,
  `artist` text DEFAULT NULL,
  `artist_unicode` text DEFAULT NULL COMMENT 'Bancho data',
  `title` text DEFAULT NULL,
  `title_unicode` text DEFAULT NULL COMMENT 'Bancho data',
  `creator` text DEFAULT NULL,
  `version` text DEFAULT NULL,
  `AudioFilename` text DEFAULT NULL,
  `PreviewTime` int(11) DEFAULT NULL,
  `BeatmapBG` text DEFAULT NULL,
  `BeatmapVideo` text DEFAULT NULL,
  `CS` float DEFAULT NULL COMMENT 'cheesegull data',
  `OD` float DEFAULT NULL COMMENT 'cheesegull data',
  `AR` float DEFAULT NULL COMMENT 'cheesegull data',
  `HP` float DEFAULT NULL COMMENT 'cheesegull data',
  `total_length` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `hit_length` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `max_combo` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `count_normal` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `count_slider` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `count_spinner` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `creator_id` int(11) DEFAULT NULL COMMENT 'Bancho data',
  `bpm` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `source` text DEFAULT NULL COMMENT 'cheesegull data',
  `tags` text DEFAULT NULL COMMENT 'cheesegull data',
  `packs` text DEFAULT NULL COMMENT 'Bancho data',
  `ranked` tinyint(1) DEFAULT NULL COMMENT 'redstar data',
  `approved` tinyint(1) DEFAULT NULL COMMENT 'Bancho data',
  `mode` tinyint(1) DEFAULT NULL COMMENT 'cheesegull data',
  `genre_id` tinyint(1) DEFAULT NULL COMMENT 'cheesegull data',
  `language_id` tinyint(1) DEFAULT NULL COMMENT 'cheesegull data',
  `storyboard` tinyint(1) DEFAULT NULL COMMENT 'cheesegull data',
  `download_unavailable` tinyint(1) DEFAULT NULL COMMENT 'cheesegull data',
  `audio_unavailable` tinyint(1) DEFAULT NULL COMMENT 'cheesegull data',
  `diff_aim` float DEFAULT NULL COMMENT 'cheesegull data',
  `diff_speed` float DEFAULT NULL COMMENT 'cheesegull data',
  `difficultyrating` float DEFAULT NULL COMMENT 'cheesegull data',
  `rating` float DEFAULT NULL COMMENT 'Bancho data',
  `favourite_count` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `playcount` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `passcount` int(11) DEFAULT NULL COMMENT 'cheesegull data',
  `submit_date` datetime DEFAULT NULL COMMENT 'Bancho data',
  `approved_date` datetime DEFAULT NULL COMMENT 'Bancho data',
  `last_update` datetime DEFAULT NULL COMMENT 'Bancho data',
  `latest_update` bigint(20) DEFAULT NULL COMMENT 'redstar data',
  `update_lock` tinyint(1) NOT NULL DEFAULT 0,
  `LastChecked` bigint(20) NOT NULL DEFAULT unix_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='osu_file_format_v, first_bid, BeatmapID, BeatmapSetID, BeatmapMD5, artist, title, creator, version, file_name,\r\nAudioFilename, PreviewTime, BeatmapBG, BeatmapVideo | cheesegull + Bancho data';

--
-- 테이블의 덤프 데이터 `beatmapsinfo`
--

INSERT INTO `beatmapsinfo` (`id`, `osu_file_format_v`, `first_bid`, `BeatmapID`, `BeatmapSetID`, `BeatmapMD5`, `file_name`, `artist`, `artist_unicode`, `title`, `title_unicode`, `creator`, `version`, `AudioFilename`, `PreviewTime`, `BeatmapBG`, `BeatmapVideo`, `CS`, `OD`, `AR`, `HP`, `total_length`, `hit_length`, `max_combo`, `count_normal`, `count_slider`, `count_spinner`, `creator_id`, `bpm`, `source`, `tags`, `packs`, `ranked`, `approved`, `mode`, `genre_id`, `language_id`, `storyboard`, `download_unavailable`, `audio_unavailable`, `diff_aim`, `diff_speed`, `difficultyrating`, `rating`, `favourite_count`, `playcount`, `passcount`, `submit_date`, `approved_date`, `last_update`, `latest_update`, `update_lock`, `LastChecked`) VALUES
(1, '14', 1919312, -1, 919187, '4a195cce8b18145cdb78747c48c8effd', '765 MILLION ALLSTARS - UNION!! (Fu3ya_) [We are all MILLION!! CS0].osu', '765 MILLION ALLSTARS', '765 MILLION ALLSTARS', 'UNION!!', 'UNION!!', 'Fu3ya_', 'We are all MILLION!! CS0', 'audio.mp3', 168382, 'TSVUNION!!.jpg', NULL, 0, 9.3, 9.2, 6, 302, 302, 1812, NULL, NULL, NULL, 5122187, 172, 'アイドルマスター ミリオンライブ！', 'アイマス ミリマス ミリシタ idolmaster 堀江晶太 imas im@s 765pro idolm@ster million live the@ter generation 11 mltd japanese idolosutrainer', 'S797', 4, 1, 0, 2, 3, 0, 0, 1, NULL, NULL, 5.37, NULL, 3428, 6677811, 461943, '2019-01-31 13:45:02', '2019-07-26 00:00:28', '2019-07-14 11:14:54', 1651742565, 1, 1715177502),
(2, '14', 2300505, -2, 1101197, '8eec990e4f38938b70d834c3dd5e99ad', '765 MILLION ALLSTARS - UNION!!(Speed Up Ver.) (Haruka_osu) [Million CS0].osu', '765 MILLION ALLSTARS', '765 MILLION ALLSTARS', 'UNION!!(Speed Up Ver.)', 'UNION!!(Speed Up Ver.)', 'Haruka_osu', 'Million CS0', 'audio.mp3', 54397, 'Konachan.com - 273868 emily_stewart group idolmaster idolmaster_million_live! kasuga_mirai nanao_yuriko tokugawa_matsuri yabuki_kana yuuki_tatsuya.jpg', NULL, 0, 9.5, 9.5, 5, 240, 240, 1720, NULL, NULL, NULL, 13660240, 215, 'アイドルマスター ミリオンライブ！', 'アイマス ミリマス ミリシタ idolmaster 堀江晶太 imas im@s 765pro idolm@ster million live the@ter generation 11 mltd japanese idolosutrainer', NULL, 4, -2, 0, 1, 1, 0, 0, 0, NULL, NULL, 5.92, NULL, 10, 7579, 694, '2020-01-29 05:52:16', NULL, '2020-07-14 04:40:09', 1639643113, 1, 1715177505),
(3, '14', 2368758, -3, 1134282, '5de8cae575d875c8cd180e0d0ae42328', '765 MILLION ALLSTARS - UNION!! (Alexsander) [Castle of Dreams CS0].osu', '765 MILLION ALLSTARS', '765 MILLION ALLSTARS', 'UNION!!', 'UNION!!', 'Alexsander', 'Castle of Dreams CS0', 'audio.mp3', 257080, 'bg.jpg', NULL, 0, 8.7, 9.2, 6.7, 305, 305, 1956, NULL, NULL, NULL, 9254241, 172, 'アイドルマスター ミリオンライブ！', 'pop video game full version アイマス ミリマス ミリシタ idolmaster 堀江晶太 imas im@s 765pro idolm@ster million live the@ter generation 11 mltd japanese idolosutrainer', 'S988', 4, 1, 0, 5, 3, 0, 0, 0, NULL, NULL, 4.91, NULL, 165, 296299, 18176, '2020-03-28 00:57:43', '2021-02-20 17:26:10', '2021-01-19 10:03:06', 1651754346, 1, 1715177506),
(4, '14', 2213673, -4, 1058213, '5e70f90dfe79c24053592c24f758dc5c', '765 MILLION ALLSTARS - UNION!! (Mak Kau Hijau) [Million Power CS0].osu', '765 MILLION ALLSTARS', '765 MILLION ALLSTARS', 'UNION!!', 'UNION!!', 'Mak Kau Hijau', 'Million Power CS0', 'audio.mp3', 168487, '851679.jpg', NULL, 0, 9, 9.2, 6.5, 304, 304, 1929, NULL, NULL, NULL, 3556629, 172, 'アイドルマスター ミリオンライブ！', 'アイマス ミリマス ミリシタ idolmaster 堀江晶太 imas im@s 765pro idolm@ster million live the@ter generation 11 mltd japanese idolosutrainer', 'S860', 4, 1, 0, 2, 3, 0, 0, 0, NULL, NULL, 5.02, NULL, 221, 339822, 38097, '2019-10-29 18:12:00', '2020-01-29 00:04:19', '2020-01-15 18:29:53', 1651754294, 1, 1715177509),
(5, '14', 47152, -5, 12483, '60d729883ea9ef56d3b4990ab8aff46f', 'Hommarju feat. Latte - masterpiece (simplistiC) [Insane CS0].osu', 'Hommarju feat. Latte', NULL, 'masterpiece', NULL, 'simplistiC', 'Insane CS0', '14 masterpiece.mp3', 179619, NULL, NULL, 0, 8, 8, 6, 183, 183, 871, NULL, NULL, NULL, 103666, 180, 'To Aru Majutsu no Index', 'ignorethis exit trance presents speed anime best 7osutrainer', 'R6,S103,T61', 4, 1, 0, 3, 3, 0, 0, 0, NULL, NULL, 4.43, NULL, 1990, 4050211, 246236, '2010-01-25 01:45:51', '2010-04-02 02:59:41', '2010-04-04 00:10:52', 1652288458, 1, 1715177511),
(6, '14', 47152, -6, 12483, '3fc0979cf06c64ea7a952fa41071b804', 'Hommarju feat. Latte - masterpiece (simplistiC) [Insane AR9].osu', 'Hommarju feat. Latte', NULL, 'masterpiece', NULL, 'simplistiC', 'Insane AR9', '14 masterpiece.mp3', 179619, NULL, NULL, 4, 8, 9, 6, 183, 183, 871, NULL, NULL, NULL, 103666, 180, 'To Aru Majutsu no Index', 'ignorethis exit trance presents speed anime best 7osutrainer', 'R6,S103,T61', 4, 1, 0, 3, 3, 0, 0, 0, NULL, NULL, 5.39, NULL, 1990, 4050211, 246236, '2010-01-25 01:45:51', '2010-04-02 02:59:41', '2010-04-04 00:10:52', 1652288458, 1, 1715177514),
(7, '14', 47152, -7, 12483, 'f3e95832ae1630b099fc9a6227f29001', 'Hommarju feat. Latte - masterpiece (simplistiC) [Insane AR10].osu', 'Hommarju feat. Latte', NULL, 'masterpiece', NULL, 'simplistiC', 'Insane AR10', '14 masterpiece.mp3', 179619, NULL, NULL, 4, 8, 10, 6, 183, 183, 871, NULL, NULL, NULL, 103666, 180, 'To Aru Majutsu no Index', 'ignorethis exit trance presents speed anime best 7osutrainer', 'R6,S103,T61', 4, 1, 0, 3, 3, 0, 0, 0, NULL, NULL, 5.39, NULL, 1990, 4050211, 246236, '2010-01-25 01:45:51', '2010-04-02 02:59:41', '2010-04-04 00:10:52', 1652288458, 1, 1715177516),
(8, '14', 2486881, -8, 1193588, '1cc6dfa5464cbc803a4e169d80c4272b', 'Yamajet feat. Hiura Masako - Sunglow (Onlybiscuit) [Harmony CS0].osu', 'Yamajet feat. Hiura Masako', 'Yamajet feat. ひうらまさこ', 'Sunglow', 'Sunglow', 'Onlybiscuit', 'Harmony CS0', 'audio.mp3', 97532, 'aawe.jpg', NULL, 0, 9.3, 9.3, 5, 301, 301, 1646, NULL, NULL, NULL, 7785535, 180, 'crossbeats REV. SUNRISE', 'happy high carolie しあわせハイカロリー capcom video game japanese female vocals full version jpop j-pop j pop brotarksosutrainer', 'S907', 4, 1, 0, 2, 3, 0, 0, 0, NULL, NULL, 5.34, NULL, 2569, 5597352, 420858, '2020-06-15 22:23:58', '2020-07-08 03:24:43', '2020-06-30 16:32:06', 1652289071, 1, 1715177518),
(9, '14', 2097898, -9, 1002271, 'f0986d45e947bf5c3cdd539842cf7c8c', 'Bliitzit - Team Magma & Aqua Leader Battle Theme (Unofficial) (Sotarks) [Catastrophe CS0].osu', 'Bliitzit', 'Bliitzit', 'Team Magma & Aqua Leader Battle Theme (Unofficial)', 'Team Magma & Aqua Leader Battle Theme (Unofficial)', 'Sotarks', 'Catastrophe CS0', 'audio.mp3', 7827, 'bg.jpg', NULL, 0, 9.2, 9.2, 6.2, 74, 74, 428, NULL, NULL, NULL, 4452992, 200, 'ポケモン オメガルビー・アルファサファイア', 'video game instrumental pokémon pokemon pocket monsters omega ruby alpha sapphire emerald oras rse battle team aqua magma 増田 順 junichi masuda edit remix 足立美奈子 黒田英明 adachi minako kuroda hideaki sentou! aqua-dan / magma-dan no leader 戦闘! アクア団・マグマ団のリーダー akitoshi corinn -laura- reform kujinn kowari smokelindosutrainer', 'S800', 4, 1, 0, 2, 5, 0, 0, 0, NULL, NULL, 5.48, NULL, 1437, 6030450, 402651, '2019-07-12 21:24:19', '2019-08-01 18:00:02', '2019-07-25 08:19:53', 1652289288, 1, 1715177520),
(10, '14', 2097898, -10, 1002271, '6ebf29e7b89f7903d5806f9645af6e7e', 'Bliitzit - Team Magma & Aqua Leader Battle Theme (Unofficial) (Sotarks) [Catastrophe AR10].osu', 'Bliitzit', 'Bliitzit', 'Team Magma & Aqua Leader Battle Theme (Unofficial)', 'Team Magma & Aqua Leader Battle Theme (Unofficial)', 'Sotarks', 'Catastrophe AR10', 'audio.mp3', 7827, 'bg.jpg', NULL, 4, 9.2, 10, 6.2, 74, 74, 428, NULL, NULL, NULL, 4452992, 200, 'ポケモン オメガルビー・アルファサファイア', 'video game instrumental pokémon pokemon pocket monsters omega ruby alpha sapphire emerald oras rse battle team aqua magma 増田 順 junichi masuda edit remix 足立美奈子 黒田英明 adachi minako kuroda hideaki sentou! aqua-dan / magma-dan no leader 戦闘! アクア団・マグマ団のリーダー akitoshi corinn -laura- reform kujinn kowari smokelindosutrainer', 'S800', 4, 1, 0, 2, 5, 0, 0, 0, NULL, NULL, 6.42, NULL, 1437, 6030450, 402651, '2019-07-12 21:24:19', '2019-08-01 18:00:02', '2019-07-25 08:19:53', 1652289288, 1, 1715177524),
(11, '14', 1642791, -11, 782318, '5d72826f592accc29bb252de1bf4346f', 'WISEMAN - The Theme of WISEMAN (Livia) [Expert CS0].osu', 'WISEMAN', 'ワイズマン (CV.原田彩楓&CV.鬼頭明里&CV.真野あゆみ)', 'The Theme of WISEMAN', 'ワイズマンのテーマ', 'Livia', 'Expert CS0', 'audio.mp3', 50028, 'DZ7YPCQVAAMkP8G.jpg', NULL, 0, 8.5, 9.6, 6, 87, 87, 789, NULL, NULL, NULL, 1298844, 154, 'ラストピリオド -終わりなき螺旋の物語-	G', 'anime endingosutrainer', NULL, 4, -2, 0, 1, 1, 0, 0, 0, NULL, NULL, 5.26, NULL, 46, 10351, 2551, '2018-05-16 15:55:49', NULL, '2018-05-18 21:52:19', 1652289552, 1, 1715177525),
(12, '14', 1821147, -12, 871623, '406c97b95441d9156137361cc5891c7a', 'xi - over the top (Unspoken Mattay) [Above the stars CS0].osu', 'xi', NULL, 'over the top', NULL, 'Unspoken Mattay', 'Above the stars CS0', 'audio.mp3', 77017, 'Konachan.com - 199485 bou_nin clouds long_hair original scenic sky.jpg', NULL, 0, 10, 9.5, 3, 115, 115, 1325, NULL, NULL, NULL, NULL, 202, '', 'osutrainer', NULL, 4, NULL, 0, 1, 1, NULL, NULL, NULL, NULL, NULL, 6.81, NULL, 8, 2377, 36, NULL, NULL, NULL, 1651799396, 1, 1715177528),
(13, '14', 1258642, -13, 595163, '14deaedc2b9f468e717d3d59efb4451e', 'Yamajet feat. Hiura Masako - Sunglow ([ Sharuresu ]) [Melody CS0].osu', 'Yamajet feat. Hiura Masako', 'Yamajet feat. ひうらまさこ', 'Sunglow', 'Sunglow', '[ Sharuresu ]', 'Melody CS0', 'audio.mp3', 97520, 'sunglowbg.png', NULL, 0, 9, 9.3, 5.5, 301, 301, 1721, NULL, NULL, NULL, 5597639, 180, 'crossbeats REV. SUNRISE', 'happy high carolie しあわせハイカロリー cross×beats capcomosutrainer', 'S555', 4, 1, 0, 2, 3, 0, 0, 0, NULL, NULL, 5.03, NULL, 1379, 3660334, 299082, '2017-04-04 23:36:53', '2017-06-23 23:00:16', '2017-06-15 13:00:05', 1652292011, 1, 1715177529),
(14, '9', 149923, -14, 48498, '55d1d64983b2f95e1dbdf28527816080', 'Hommarju feat. Latte - masterpiece (Zapy) [SQUARES].osu', 'Hommarju feat. Latte', NULL, 'masterpiece', NULL, 'ThunderSRM', 'SQUARES', '14 masterpiece.mp3', 179619, 'untitled3.jpg', NULL, 4, 8, 8, 6, 211, 211, 1252, NULL, NULL, NULL, 890975, 180, 'To Aru Majutsu no Index', 'simplistic\'s squares zapyosutrainer', NULL, 4, -2, 0, 1, 1, 1, 0, 0, NULL, NULL, 5.42, NULL, 6, 207, 1, '2012-04-10 05:06:56', NULL, '2012-04-10 05:37:30', 0, 1, 1715177533),
(15, '14', 1702971, -15, 811908, '5ef5d9927903e2da29c4409622734e6d', 'Hana - Sakura no Uta (Sped Up Ver.) (tsundereSam) [Sakura Seed CS0].osu', 'Hana', 'はな', 'Sakura no Uta (Sped Up Ver.)', '櫻ノ詩 (Sped Up Ver.)', 'tsundereSam', 'Sakura Seed CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 0, 8.8, 9.8, 5, 181, 181, 1336, NULL, NULL, NULL, 6357685, 207, 'サクラノ詩 -櫻の森の上を舞う-', 'quantumvortex sammie -sakura no mori no ue o mau- metrowing 枕 makura eroge galgame video game rock japaneseosutrainer', 'SL99', 4, 4, 0, 2, 3, 0, 0, 1, NULL, NULL, 6.83944, NULL, 1572, 1003591, 73339, '2018-07-10 13:22:55', '2021-05-24 23:21:47', '2021-05-07 12:23:14', 1662047540, 1, 1715177535),
(16, '14', 1702971, -16, 811908, '4733b8c5d32514750124da24da511195', 'Hana - Sakura no Uta (Sped Up Ver.) (ts... [Triangle-chan\'s Sakura Tree CS0].osu', 'Hana', 'はな', 'Sakura no Uta (Sped Up Ver.)', '櫻ノ詩 (Sped Up Ver.)', 'tsundereSam', 'Triangle-chan\'s Sakura Tree CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 0, 9, 9.8, 5, 200, 200, 1506, NULL, NULL, NULL, 6357685, 207, 'サクラノ詩 -櫻の森の上を舞う-', 'quantumvortex sammie -sakura no mori no ue o mau- metrowing 枕 makura eroge galgame video game rock japaneseosutrainer', 'SL99', 4, 4, 0, 2, 3, 0, 0, 1, NULL, NULL, 7.74496, NULL, 1572, 250930, 14087, '2018-07-10 13:22:55', '2021-05-24 23:21:47', '2021-05-07 12:23:14', 1662047544, 1, 1715177538),
(17, '14', 1702971, -17, 811908, '1fdaad4c2b3b6622b1ffa84e9cf7ba68', 'Hana - Sakura no Uta (Sped Up Ver.) (ts...ex\'s Thousand Cherry Blossoms CS0].osu', 'Hana', 'はな', 'Sakura no Uta (Sped Up Ver.)', '櫻ノ詩 (Sped Up Ver.)', 'tsundereSam', 'quantumvortex\'s Thousand Cherry Blossoms CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 0, 9.8, 9.9, 3.9, 200, 200, 1355, NULL, NULL, NULL, 6357685, 207, 'サクラノ詩 -櫻の森の上を舞う-', 'quantumvortex sammie -sakura no mori no ue o mau- metrowing 枕 makura eroge galgame video game rock japaneseosutrainer', 'SL99', 4, 4, 0, 2, 3, 0, 0, 1, NULL, NULL, 7.82071, NULL, 1572, 126964, 8087, '2018-07-10 13:22:55', '2021-05-24 23:21:47', '2021-05-07 12:23:14', 1662047547, 1, 1715177541),
(18, '14', 1702971, -18, 811908, 'f2de95b0c33633453dcb79b85944e851', 'Hana - Sakura no Uta (Sped Up Ver.) (ts...ura Tree will last Forever... CS0].osu', 'Hana', 'はな', 'Sakura no Uta (Sped Up Ver.)', '櫻ノ詩 (Sped Up Ver.)', 'tsundereSam', 'This Final Verse of the Sakura Tree will last Forever... CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 0, 9.2, 10, 5.5, 200, 200, 1543, NULL, NULL, NULL, 6357685, 207, 'サクラノ詩 -櫻の森の上を舞う-', 'quantumvortex sammie -sakura no mori no ue o mau- metrowing 枕 makura eroge galgame video game rock japaneseosutrainer', 'SL99', 4, 4, 0, 2, 3, 0, 0, 1, NULL, NULL, 7.97992, NULL, 1572, 267643, 14390, '2018-07-10 13:22:55', '2021-05-24 23:21:47', '2021-05-07 12:23:14', 1662047550, 1, 1715177543),
(19, '14', -19, -19, -10000000, '1cd28651e85cf135ba991259bed7158d', 'Nomizu Iori - Black + White (TV Size) (arpia97) [ULTIMATE STAR BURST!!!].osu', 'Nomizu Iori', NULL, 'Black + White (TV Size)', NULL, 'arpia97', 'ULTIMATE STAR BURST!!!', 'Black White.mp3', 62729, 'thumb-1920-671473.jpg', NULL, -1, 0, 0, 7, 0, 0, 2520, NULL, NULL, NULL, NULL, 192, 'Mondaiji-tachi ga Isekai kara Kuru Sou Desu yo?', 'momochi dakedekaane xinely hinsvar kuro usagi bunny girl asuka you izayoi adaption novel opening osutrainerosutrainer', NULL, 4, NULL, 3, -1, -3, NULL, NULL, NULL, NULL, NULL, 40.52, NULL, -1, -1, -1, NULL, NULL, NULL, 1679680595, 1, 1715177544),
(20, '14', 305947, -20, 119103, '0f28be881f56ad92d026fbb1c6470e55', 'goreshit - fly, heart!  fly! (eLy) [vs ELY Over Stream CS0].osu', 'goreshit', 'goreshit', 'fly, heart!  fly!', 'fly, heart!  fly!', 'eLy', 'vs ELY Over Stream CS0', 'MG.mp3', 114973, 'BG.jpg', NULL, 0, 7, 9, 6, 170, 170, 1377, NULL, NULL, NULL, 1014222, 201, 'Flyable Heart', 'flyable fly heart stream over goreshit ely featured artistosutrainer', 'SL78', 4, 4, 0, 10, 3, 0, 0, 0, NULL, NULL, 5.65, NULL, 561, 157572, 5940, '2013-09-26 18:45:41', '2019-11-06 01:07:16', '2013-09-26 18:49:17', 1670966605, 1, 1715177548),
(21, '14', 305947, -21, 119103, '4b5eb6b6eade7d77e9f3c34451ae295d', 'goreshit - fly, heart!  fly! (eLy) [vs ELY Over Stream (AR10) CS0].osu', 'goreshit', 'goreshit', 'fly, heart!  fly!', 'fly, heart!  fly!', 'eLy', 'vs ELY Over Stream (AR10) CS0', 'MG.mp3', 114973, 'BG.jpg', NULL, 0, 7, 10, 6, 170, 170, 1377, NULL, NULL, NULL, 1014222, 201, 'Flyable Heart', 'flyable fly heart stream over goreshit ely featured artistosutrainer', 'SL78', 4, 4, 0, 10, 3, 0, 0, 0, NULL, NULL, 5.65, NULL, 561, 365049, 20178, '2013-09-26 18:45:41', '2019-11-06 01:07:16', '2013-09-26 18:49:17', 1670966603, 1, 1715177550),
(22, '14', 47152, -22, 12483, '87690e37e0e2fd39c9b0d9b872ce8d64', 'Hommarju feat. Latte - masterpiece (simplistiC) [ignore\'s Chaos AR10].osu', 'Hommarju feat. Latte', NULL, 'masterpiece', NULL, 'simplistiC', 'ignore\'s Chaos AR10', '14 masterpiece.mp3', 179619, NULL, NULL, 4, 8, 10, 7, 157, 157, 730, NULL, NULL, NULL, 103666, 180, 'To Aru Majutsu no Index', 'ignorethis exit trance presents speed anime best 7osutrainer', 'R6,S103,T61', 4, 1, 0, 3, 3, 0, 0, 0, NULL, NULL, 4.5, NULL, 1990, 1909716, 162468, '2010-01-25 01:45:51', '2010-04-02 02:59:41', '2010-04-04 00:10:52', 1693719551, 1, 1715177554),
(23, '14', 1963885, -23, 940322, '0ac0c334dca3cbb3d38fa0567309b56d', 'Komichi Aya (CV Taneda Risa) - Koiiro Iris (brz_bootleg_remix) (shinchikuhome) [Inner Oni Kiai1].osu', 'Komichi Aya (CV: Taneda Risa)', '小路 綾 (CV: 種田 梨沙)', 'Koiiro Iris (brz_bootleg_remix)', 'こいいろアイリス (brz_bootleg_remix)', 'shinchikuhome', 'Inner Oni Kiai1', 'audio.mp3', 48841, 'BG.jpg', NULL, 5, 7, 5, 4, 210, 208, 281, NULL, NULL, NULL, 3174184, 310, 'ハロー！！きんいろモザイク', 'hello!! kiniro mosaic kinmoza character song music palette 2 きんモザ brz bootleg remix japanese j-pop anime', NULL, 5, 4, 1, 10, 3, 0, 0, 0, NULL, NULL, 6.4, NULL, 157, 0, 0, '2019-03-15 07:46:31', '2021-11-01 18:57:17', '2021-10-31 23:52:01', 1702152306, 1, 1715177556),
(24, '14', 1963885, -24, 940322, 'cd39c5796c8a0f894522f00db62c6270', 'Komichi Aya (CV Taneda Risa) - Koiiro Iris (brz_bootleg_remix) (shinchikuhome) [Inner Oni Kiai2].osu', 'Komichi Aya (CV: Taneda Risa)', '小路 綾 (CV: 種田 梨沙)', 'Koiiro Iris (brz_bootleg_remix)', 'こいいろアイリス (brz_bootleg_remix)', 'shinchikuhome', 'Inner Oni Kiai2', 'audio.mp3', 48841, 'BG.jpg', NULL, 5, 7, 5, 4, 210, 208, 282, NULL, NULL, NULL, 3174184, 310, 'ハロー！！きんいろモザイク', 'hello!! kiniro mosaic kinmoza character song music palette 2 きんモザ brz bootleg remix japanese j-pop anime', NULL, 5, 4, 1, 10, 3, 0, 0, 0, NULL, NULL, 6.37, NULL, 157, 0, 0, '2019-03-15 07:46:31', '2021-11-01 18:57:17', '2021-10-31 23:52:01', 1702152306, 1, 1715177558),
(25, '14', 1963885, -25, 940322, '8739c130d92e523bd08344fb644b7a9d', 'Komichi Aya (CV Taneda Risa) - Koiiro Iris (brz_bootleg_remix) (shinchikuhome) [Inner Oni Kiai3].osu', 'Komichi Aya (CV: Taneda Risa)', '小路 綾 (CV: 種田 梨沙)', 'Koiiro Iris (brz_bootleg_remix)', 'こいいろアイリス (brz_bootleg_remix)', 'shinchikuhome', 'Inner Oni Kiai3', 'audio.mp3', 48841, 'BG.jpg', NULL, 5, 7, 5, 4, 210, 208, 298, NULL, NULL, NULL, 3174184, 310, 'ハロー！！きんいろモザイク', 'hello!! kiniro mosaic kinmoza character song music palette 2 きんモザ brz bootleg remix japanese j-pop anime', NULL, 5, 4, 1, 10, 3, 0, 0, 0, NULL, NULL, 6.69, NULL, 157, 0, 0, '2019-03-15 07:46:31', '2021-11-01 18:57:17', '2021-10-31 23:52:01', 1702152306, 1, 1715177560),
(26, '14', 4140097, -26, 1992444, '470435403473c25327f34c435911b9e3', 'DJ SHARPNEL - FUWANITY (Kettle) [Shiawase 1.26x (240bpm) AR10.3].osu', 'DJ SHARPNEL', 'DJ SHARPNEL', 'FUWANITY', 'FUWANITY', 'Kettle', 'Shiawase 1.26x (240bpm) AR10.3', 'audio 1.258x withDT.mp3', 156749, 'background name.jpg', NULL, 4, 8.2, 9, 5, 230, 192, 2160, NULL, NULL, NULL, 18322271, 191, 'けいおん！', 'fuwatanity electronic japanese anime k-on! sharpnelsound hardcore j-core 妄殺オタクティクス srpc-0024 htt 放課後ティータイム k on houkago tea time ho-kago hirasawa yui 平沢 唯 akiyama mio 秋山 澪 tainaka ritsu 田井中 律 kotobuki tsumugi 琴吹 紬 toyosaki aki 豊崎 愛生 hikasa youko 日笠 陽子 satou satomi 佐藤 聡美 kotobuki minako 寿 美菜子 jcore hokago bootleg remix fuwa fuwa time ふわふわ時間', NULL, 4, 0, 0, 1, 1, 0, 0, 0, NULL, NULL, 5.64, NULL, 2, 0, 0, '2023-05-14 16:05:27', NULL, '2024-04-12 17:42:58', 1710085960, 1, 1715177562),
(27, '14', 4140097, -27, 1992444, '379e5b60b00b2948302d7d7151db6979', 'DJ SHARPNEL - FUWANITY (Kettle) [33].osu', 'DJ SHARPNEL', 'DJ SHARPNEL', 'FUWANITY', 'FUWANITY', 'Kettle', '33', 'audio 1.258x withDT.mp3', 156749, 'background name.jpg', NULL, 4, 8.2, 9, 5, 0, 0, 0, NULL, NULL, NULL, 18322271, 191, 'けいおん！', 'fuwatanity electronic japanese anime k-on! sharpnelsound hardcore j-core 妄殺オタクティクス srpc-0024 htt 放課後ティータイム k on houkago tea time ho-kago hirasawa yui 平沢 唯 akiyama mio 秋山 澪 tainaka ritsu 田井中 律 kotobuki tsumugi 琴吹 紬 toyosaki aki 豊崎 愛生 hikasa youko 日笠 陽子 satou satomi 佐藤 聡美 kotobuki minako 寿 美菜子 jcore hokago bootleg remix fuwa fuwa time ふわふわ時間', NULL, 4, 0, 0, 1, 1, 0, 0, 0, NULL, NULL, 5.62, NULL, 2, 0, 0, '2023-05-14 16:05:27', NULL, '2024-04-12 17:42:58', 1710085960, 1, 1715177564),
(28, '14', 1639118, -1639118, 780250, 'bd7be54e98810120eae718383892e8ed', 'Alfakyun. - Teo (-Light-) [Nothing will stop us].osu', 'Alfakyun.', '＋α／あるふぁきゅん。', 'Teo', 'テオ', 'netnesanya', 'Nothing will stop us', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 4.2, 9, 9.7, 6, 189, 189, 1350, NULL, NULL, NULL, 6017901, 185, '', '-light- shirasaka koume rollpan wajinshu 歌ってみた utattemita 歌い手 utaite cover japanese rock vocaloid 初音ミク hatsune miku synth first waltz omoi rootage a rootage/α alphaosutrainer', NULL, 3, 4, 0, 4, 3, 0, 0, 0, NULL, NULL, 6.68087, NULL, 1439, 133975, 14378, '2018-05-12 18:02:27', '2022-08-05 08:29:59', '2022-07-29 22:25:09', 0, 1, 1715177567),
(29, '14', 1639118, -1639687, 780250, '2697d9ce593a95b23b7721f311134ecb', 'Alfakyun. - Teo (-Light-) [Insane].osu', 'Alfakyun.', '＋α／あるふぁきゅん。', 'Teo', 'テオ', 'netnesanya', 'Insane', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 4, 8, 9, 5.5, 189, 189, 1299, NULL, NULL, NULL, 6017901, 185, '', '-light- shirasaka koume rollpan wajinshu 歌ってみた utattemita 歌い手 utaite cover japanese rock vocaloid 初音ミク hatsune miku synth first waltz omoi rootage a rootage/α alphaosutrainer', NULL, 3, 4, 0, 4, 3, 0, 0, 0, NULL, NULL, 5.23866, NULL, 1439, 177256, 40842, '2018-05-12 18:02:27', '2022-08-05 08:29:59', '2022-07-29 22:25:09', 0, 1, 1715177571),
(30, '14', 1639118, -1645802, 780250, '707ecd7e32b4b17b5fd3cd6e337ad21e', 'Alfakyun. - Teo (-Light-) [Collab Light Insane].osu', 'Alfakyun.', '＋α／あるふぁきゅん。', 'Teo', 'テオ', 'netnesanya', 'Collab Light Insane', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 4, 7, 8.8, 5, 193, 193, 1137, NULL, NULL, NULL, 6017901, 185, '', '-light- shirasaka koume rollpan wajinshu 歌ってみた utattemita 歌い手 utaite cover japanese rock vocaloid 初音ミク hatsune miku synth first waltz omoi rootage a rootage/α alphaosutrainer', NULL, 3, 4, 0, 4, 3, 0, 0, 0, NULL, NULL, 4.64741, NULL, 1439, 125299, 28696, '2018-05-12 18:02:27', '2022-08-05 08:29:59', '2022-07-29 22:25:09', 0, 1, 1715177573),
(31, '14', 1639118, -1648943, 780250, 'efdfbb02094c6ddbee8aad9f175546cb', 'Alfakyun. - Teo (-Light-) [waji\'s Normal].osu', 'Alfakyun.', '＋α／あるふぁきゅん。', 'Teo', 'テオ', 'netnesanya', 'waji\'s Normal', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 3.2, 3, 4.3, 3, 173, 173, 576, NULL, NULL, NULL, 6017901, 185, '', '-light- shirasaka koume rollpan wajinshu 歌ってみた utattemita 歌い手 utaite cover japanese rock vocaloid 初音ミク hatsune miku synth first waltz omoi rootage a rootage/α alphaosutrainer', NULL, 3, 4, 0, 4, 3, 0, 0, 0, NULL, NULL, 2.29277, NULL, 1439, 26362, 9633, '2018-05-12 18:02:27', '2022-08-05 08:29:59', '2022-07-29 22:25:09', 0, 1, 1715177576),
(32, '14', 1639118, -1653038, 780250, 'ef772374bbd27319c550e3f4365789e8', 'Alfakyun. - Teo (-Light-) [Koume\'s Extra].osu', 'Alfakyun.', '＋α／あるふぁきゅん。', 'Teo', 'テオ', 'netnesanya', 'Koume\'s Extra', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 4, 8.5, 9.4, 6, 188, 188, 1279, NULL, NULL, NULL, 6017901, 185, '', '-light- shirasaka koume rollpan wajinshu 歌ってみた utattemita 歌い手 utaite cover japanese rock vocaloid 初音ミク hatsune miku synth first waltz omoi rootage a rootage/α alphaosutrainer', NULL, 3, 4, 0, 4, 3, 0, 0, 0, NULL, NULL, 6.16845, NULL, 1439, 128593, 10799, '2018-05-12 18:02:27', '2022-08-05 08:29:59', '2022-07-29 22:25:09', 0, 1, 1715177580),
(33, '14', 1639118, -1655703, 780250, 'c45a206bbfd3550062127ca23db7a601', 'Alfakyun. - Teo (-Light-) [Hard].osu', 'Alfakyun.', '＋α／あるふぁきゅん。', 'Teo', 'テオ', 'netnesanya', 'Hard', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 3.8, 6, 8, 5, 189, 189, 1095, NULL, NULL, NULL, 6017901, 185, '', '-light- shirasaka koume rollpan wajinshu 歌ってみた utattemita 歌い手 utaite cover japanese rock vocaloid 初音ミク hatsune miku synth first waltz omoi rootage a rootage/α alphaosutrainer', NULL, 3, 4, 0, 4, 3, 0, 0, 0, NULL, NULL, 3.66436, NULL, 1439, 69643, 18836, '2018-05-12 18:02:27', '2022-08-05 08:29:59', '2022-07-29 22:25:09', 0, 1, 1715177583),
(34, '14', 2149349, -2160333, 1027900, '08d928047d5be504f2e088cc6e4b6e4f', 't+pazolite - Party in the HOLLOWood feat. Nanahira (HOLLOWeen Sitchaka Metchaka Remix) (_Asha) [Rabbit Lude\'s Hard].osu', 't+pazolite', 't+pazolite', 'Party in the HOLLOWood feat. Nanahira (HOLLOWeen Sitchaka Metchaka Remix)', 'Party in the HOLLOWood feat. ななひら (HOLLOWeen Sitchaka Metchaka Remix)', '_Asha', 'Rabbit Lude\'s Hard', 'audio.mp3', 42005, 'haloween.jpg', NULL, 4, 8.3, 0, 7.7, 195, 195, 0, NULL, NULL, NULL, 11103764, 200, 'Muse Dash', 'lude interlude- hoto cocoa leqek famoss electronic hardcore j-core japanese core jcore chs-0031 good evening evening hollowood. tpazolite tpz happy otaku pack vol. 13osutrainer', 'SM109', 3, 1, 3, 10, 3, 0, 0, 0, NULL, NULL, 3.54, NULL, 736, 71218, 15442, '2019-08-26 09:05:22', '2022-04-09 13:01:45', '2022-04-02 10:58:14', 0, 1, 1715177586),
(35, '14', 3917272, -3917272, 1900394, '64ce780a48fe717ab454008452d78fec', 'katagiri - STRONG 280 (mokumoku-) [TURBULENT~!].osu', 'katagiri', 'かたぎり', 'STRONG 280', 'STRONG 280', 'mokumoku-', 'TURBULENT~!', 'audio.mp3', 212518, '1228547.jpg', NULL, -1, 9, 10, -1, 127, 127, 1322, NULL, NULL, NULL, 12301910, 280, 'KAKUSATSU SHOUJO', 'osutrainerosutrainer', NULL, 3, -2, 0, 10, 3, 0, 0, 0, NULL, NULL, 8.20301, NULL, 2, -1, -1, '2022-12-10 00:43:09', NULL, '2023-09-27 04:14:01', 1707923041, 1, 1715177589);

--
-- 덤프된 테이블의 인덱스
--

--
-- 테이블의 인덱스 `beatmapsinfo`
--
ALTER TABLE `beatmapsinfo`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `BeatmapMD5` (`BeatmapMD5`),
  ADD KEY `BeatmapID` (`BeatmapID`) USING BTREE,
  ADD KEY `BeatmapSetID` (`BeatmapSetID`) USING BTREE,
  ADD KEY `artist` (`artist`(768)) USING BTREE,
  ADD KEY `title` (`title`(768)) USING BTREE,
  ADD KEY `creator` (`creator`(768)) USING BTREE,
  ADD KEY `version` (`version`(768)) USING BTREE,
  ADD KEY `file_name` (`file_name`(768)) USING BTREE,
  ADD KEY `source` (`source`(768)) USING BTREE,
  ADD KEY `tags` (`tags`(768)) USING BTREE,
  ADD KEY `packs` (`packs`(768)) USING BTREE,
  ADD KEY `artist_unicode` (`artist_unicode`(768)) USING BTREE,
  ADD KEY `title_unicode` (`title_unicode`(768)) USING BTREE;

--
-- 덤프된 테이블의 AUTO_INCREMENT
--

--
-- 테이블의 AUTO_INCREMENT `beatmapsinfo`
--
ALTER TABLE `beatmapsinfo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
