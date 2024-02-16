-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- 생성 시간: 24-02-15 21:21
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
CREATE DATABASE IF NOT EXISTS `osu_media_server` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `osu_media_server`;

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
  `title` text DEFAULT NULL,
  `creator` text DEFAULT NULL,
  `version` text DEFAULT NULL,
  `AudioFilename` text DEFAULT NULL,
  `PreviewTime` int(11) DEFAULT NULL,
  `BeatmapBG` text DEFAULT NULL,
  `BeatmapVideo` text DEFAULT NULL,
  `last_update` bigint(20) NOT NULL DEFAULT unix_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='first_bid, BeatmapID, BeatmapSetID, BeatmapMD5, artist, title, creator, version, file_name,\r\nAudioFilename, PreviewTime, BeatmapBG, BeatmapVideo';

--
-- 테이블의 덤프 데이터 `beatmapsinfo`
--

INSERT INTO `beatmapsinfo` (`id`, `osu_file_format_v`, `first_bid`, `BeatmapID`, `BeatmapSetID`, `BeatmapMD5`, `file_name`, `artist`, `title`, `creator`, `version`, `AudioFilename`, `PreviewTime`, `BeatmapBG`, `BeatmapVideo`, `last_update`) VALUES
(1, '14', 1919312, -1, 919187, '4a195cce8b18145cdb78747c48c8effd', '765 MILLION ALLSTARS - UNION!! (Fu3ya_) [We are all MILLION!! CS0].osu', '765 MILLION ALLSTARS', 'UNION!!', 'Fu3ya_', 'We are all MILLION!! CS0', 'audio.mp3', 168382, 'TSVUNION!!.jpg', NULL, 1708028262),
(2, '14', 2300505, -2, 1101197, '8eec990e4f38938b70d834c3dd5e99ad', '765 MILLION ALLSTARS - UNION!!(Speed Up Ver.) (Haruka_osu) [Million CS0].osu', '765 MILLION ALLSTARS', 'UNION!!(Speed Up Ver.)', 'Haruka_osu', 'Million CS0', 'audio.mp3', 54397, 'Konachan.com - 273868 emily_stewart group idolmaster idolmaster_million_live! kasuga_mirai nanao_yuriko tokugawa_matsuri yabuki_kana yuuki_tatsuya.jpg', NULL, 1708028264),
(3, '14', 2368758, -3, 1134282, '5de8cae575d875c8cd180e0d0ae42328', '765 MILLION ALLSTARS - UNION!! (Alexsander) [Castle of Dreams CS0].osu', '765 MILLION ALLSTARS', 'UNION!!', 'Alexsander', 'Castle of Dreams CS0', 'audio.mp3', 257080, 'bg.jpg', NULL, 1708028267),
(4, '14', 2213673, -4, 1058213, '5e70f90dfe79c24053592c24f758dc5c', '765 MILLION ALLSTARS - UNION!! (Mak Kau Hijau) [Million Power CS0].osu', '765 MILLION ALLSTARS', 'UNION!!', 'Mak Kau Hijau', 'Million Power CS0', 'audio.mp3', 168487, '851679.jpg', NULL, 1708028268),
(5, '14', 47152, -5, 12483, '60d729883ea9ef56d3b4990ab8aff46f', 'Hommarju feat. Latte - masterpiece (simplistiC) [Insane CS0].osu', 'Hommarju feat. Latte', 'masterpiece', 'simplistiC', 'Insane CS0', '14 masterpiece.mp3', 179619, NULL, NULL, 1708028272),
(6, '14', 47152, -6, 12483, '3fc0979cf06c64ea7a952fa41071b804', 'Hommarju feat. Latte - masterpiece (simplistiC) [Insane AR9].osu', 'Hommarju feat. Latte', 'masterpiece', 'simplistiC', 'Insane AR9', '14 masterpiece.mp3', 179619, NULL, NULL, 1708028276),
(7, '14', 47152, -7, 12483, 'f3e95832ae1630b099fc9a6227f29001', 'Hommarju feat. Latte - masterpiece (simplistiC) [Insane AR10].osu', 'Hommarju feat. Latte', 'masterpiece', 'simplistiC', 'Insane AR10', '14 masterpiece.mp3', 179619, NULL, NULL, 1708028282),
(8, '14', 2486881, -8, 1193588, '1cc6dfa5464cbc803a4e169d80c4272b', 'Yamajet feat. Hiura Masako - Sunglow (Onlybiscuit) [Harmony CS0].osu', 'Yamajet feat. Hiura Masako', 'Sunglow', 'Onlybiscuit', 'Harmony CS0', 'audio.mp3', 97532, 'aawe.jpg', NULL, 1708028284),
(9, '14', 2097898, -9, 1002271, 'f0986d45e947bf5c3cdd539842cf7c8c', 'Bliitzit - Team Magma & Aqua Leader Battle Theme (Unofficial) (Sotarks) [Catastrophe CS0].osu', 'Bliitzit', 'Team Magma & Aqua Leader Battle Theme (Unofficial)', 'Sotarks', 'Catastrophe CS0', 'audio.mp3', 7827, 'bg.jpg', NULL, 1708028285),
(10, '14', 2097898, -10, 1002271, '6ebf29e7b89f7903d5806f9645af6e7e', 'Bliitzit - Team Magma & Aqua Leader Battle Theme (Unofficial) (Sotarks) [Catastrophe AR10].osu', 'Bliitzit', 'Team Magma & Aqua Leader Battle Theme (Unofficial)', 'Sotarks', 'Catastrophe AR10', 'audio.mp3', 7827, 'bg.jpg', NULL, 1708028288),
(11, '14', 1642791, -11, 782318, '5d72826f592accc29bb252de1bf4346f', 'WISEMAN - The Theme of WISEMAN (Livia) [Expert CS0].osu', 'WISEMAN', 'The Theme of WISEMAN', 'Livia', 'Expert CS0', 'audio.mp3', 50028, 'DZ7YPCQVAAMkP8G.jpg', NULL, 1708028290),
(12, '14', 1821147, -12, 871623, '406c97b95441d9156137361cc5891c7a', 'xi - over the top (Unspoken Mattay) [Above the stars CS0].osu', 'xi', 'over the top', 'Unspoken Mattay', 'Above the stars CS0', 'audio.mp3', 77017, 'Konachan.com - 199485 bou_nin clouds long_hair original scenic sky.jpg', NULL, 1708028293),
(13, '14', 1258642, -13, 595163, '14deaedc2b9f468e717d3d59efb4451e', 'Yamajet feat. Hiura Masako - Sunglow ([ Sharuresu ]) [Melody CS0].osu', 'Yamajet feat. Hiura Masako', 'Sunglow', '[ Sharuresu ]', 'Melody CS0', 'audio.mp3', 97520, 'sunglowbg.png', NULL, 1708028296),
(14, '9', 149923, -14, 48498, '55d1d64983b2f95e1dbdf28527816080', 'Hommarju feat. Latte - masterpiece (Zapy) [SQUARES].osu', 'Hommarju feat. Latte', 'masterpiece', 'ThunderSRM', 'SQUARES', '14 masterpiece.mp3', 179619, NULL, NULL, 1708028302),
(15, '14', 1702971, -15, 811908, '5ef5d9927903e2da29c4409622734e6d', 'Hana - Sakura no Uta (Sped Up Ver.) (tsundereSam) [Sakura Seed CS0].osu', 'Hana', 'Sakura no Uta (Sped Up Ver.)', 'tsundereSam', 'Sakura Seed CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 1708028306),
(16, '14', 1702971, -16, 811908, '4733b8c5d32514750124da24da511195', 'Hana - Sakura no Uta (Sped Up Ver.) (ts... [Triangle-chan\'s Sakura Tree CS0].osu', 'Hana', 'Sakura no Uta (Sped Up Ver.)', 'tsundereSam', 'Triangle-chan\'s Sakura Tree CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 1708028310),
(17, '14', 1702971, -17, 811908, '1fdaad4c2b3b6622b1ffa84e9cf7ba68', 'Hana - Sakura no Uta (Sped Up Ver.) (ts...ex\'s Thousand Cherry Blossoms CS0].osu', 'Hana', 'Sakura no Uta (Sped Up Ver.)', 'tsundereSam', 'quantumvortex\'s Thousand Cherry Blossoms CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 1708028315),
(18, '14', 1702971, -18, 811908, 'f2de95b0c33633453dcb79b85944e851', 'Hana - Sakura no Uta (Sped Up Ver.) (ts...ura Tree will last Forever... CS0].osu', 'Hana', 'Sakura no Uta (Sped Up Ver.)', 'tsundereSam', 'This Final Verse of the Sakura Tree will last Forever... CS0', 'audio.mp3', 149564, '293440-anime-anime_girls-Sakura_no_Uta-Misakura_Rin.jpg', NULL, 1708028326),
(19, '14', -19, -19, -10000000, '1cd28651e85cf135ba991259bed7158d', 'Nomizu Iori - Black + White (TV Size) (arpia97) [ULTIMATE STAR BURST!!!].osu', 'Nomizu Iori', 'Black + White (TV Size)', 'arpia97', 'ULTIMATE STAR BURST!!!', 'Black White.mp3', 62729, 'thumb-1920-671473.jpg', NULL, 1708028327),
(20, '14', 305947, -20, 119103, '0f28be881f56ad92d026fbb1c6470e55', 'goreshit - fly, heart!  fly! (eLy) [vs ELY Over Stream CS0].osu', 'goreshit', 'fly, heart!  fly!', 'eLy', 'vs ELY Over Stream CS0', 'MG.mp3', 114973, 'BG.jpg', NULL, 1708028330),
(21, '14', 305947, -21, 119103, '4b5eb6b6eade7d77e9f3c34451ae295d', 'goreshit - fly, heart!  fly! (eLy) [vs ELY Over Stream (AR10) CS0].osu', 'goreshit', 'fly, heart!  fly!', 'eLy', 'vs ELY Over Stream (AR10) CS0', 'MG.mp3', 114973, 'BG.jpg', NULL, 1708028332),
(22, '14', 47152, -22, 12483, '87690e37e0e2fd39c9b0d9b872ce8d64', 'Hommarju feat. Latte - masterpiece (simplistiC) [ignore\'s Chaos AR10].osu', 'Hommarju feat. Latte', 'masterpiece', 'simplistiC', 'ignore\'s Chaos AR10', '14 masterpiece.mp3', 179619, NULL, NULL, 1708028336),
(23, '14', 1963885, -23, 940322, '0ac0c334dca3cbb3d38fa0567309b56d', 'Komichi Aya (CV Taneda Risa) - Koiiro Iris (brz_bootleg_remix) (shinchikuhome) [Inner Oni Kiai1].osu', 'Komichi Aya (CV: Taneda Risa)', 'Koiiro Iris (brz_bootleg_remix)', 'shinchikuhome', 'Inner Oni Kiai1', 'audio.mp3', 48841, 'BG.jpg', NULL, 1708028337),
(24, '14', 1963885, -24, 940322, 'cd39c5796c8a0f894522f00db62c6270', 'Komichi Aya (CV Taneda Risa) - Koiiro Iris (brz_bootleg_remix) (shinchikuhome) [Inner Oni Kiai2].osu', 'Komichi Aya (CV: Taneda Risa)', 'Koiiro Iris (brz_bootleg_remix)', 'shinchikuhome', 'Inner Oni Kiai2', 'audio.mp3', 48841, 'BG.jpg', NULL, 1708028338),
(25, '14', 1963885, -25, 940322, '8739c130d92e523bd08344fb644b7a9d', 'Komichi Aya (CV Taneda Risa) - Koiiro Iris (brz_bootleg_remix) (shinchikuhome) [Inner Oni Kiai3].osu', 'Komichi Aya (CV: Taneda Risa)', 'Koiiro Iris (brz_bootleg_remix)', 'shinchikuhome', 'Inner Oni Kiai3', 'audio.mp3', 48841, 'BG.jpg', NULL, 1708028339),
(26, '14', 1639118, -1639118, 780250, 'bd7be54e98810120eae718383892e8ed', 'Alfakyun. - Teo (-Light-) [Nothing will stop us].osu', 'Alfakyun.', 'Teo', 'netnesanya', 'Nothing will stop us', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 1708028343),
(27, '14', 1639118, -1639687, 780250, '2697d9ce593a95b23b7721f311134ecb', 'Alfakyun. - Teo (-Light-) [Insane].osu', 'Alfakyun.', 'Teo', 'netnesanya', 'Insane', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 1708028347),
(28, '14', 1639118, -1645802, 780250, '707ecd7e32b4b17b5fd3cd6e337ad21e', 'Alfakyun. - Teo (-Light-) [Collab Light Insane].osu', 'Alfakyun.', 'Teo', 'netnesanya', 'Collab Light Insane', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 1708028352),
(29, '14', 1639118, -1648943, 780250, 'efdfbb02094c6ddbee8aad9f175546cb', 'Alfakyun. - Teo (-Light-) [waji\'s Normal].osu', 'Alfakyun.', 'Teo', 'netnesanya', 'waji\'s Normal', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 1708028357),
(30, '14', 1639118, -1653038, 780250, 'ef772374bbd27319c550e3f4365789e8', 'Alfakyun. - Teo (-Light-) [Koume\'s Extra].osu', 'Alfakyun.', 'Teo', 'netnesanya', 'Koume\'s Extra', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 1708028362),
(31, '14', 1639118, -1655703, 780250, 'c45a206bbfd3550062127ca23db7a601', 'Alfakyun. - Teo (-Light-) [Hard].osu', 'Alfakyun.', 'Teo', 'netnesanya', 'Hard', 'audio.mp3', 142810, 'Konachan.com - 264137 choker dark dress hatsune_miku long_hair music paper twintails vocaloid yyb.jpg', NULL, 1708028366),
(32, '14', 2149349, -2160333, 1027900, '08d928047d5be504f2e088cc6e4b6e4f', 't+pazolite - Party in the HOLLOWood feat. Nanahira (HOLLOWeen Sitchaka Metchaka Remix) (_Asha) [Rabbit Lude\'s Hard].osu', 't+pazolite', 'Party in the HOLLOWood feat. Nanahira (HOLLOWeen Sitchaka Metchaka Remix)', '_Asha', 'Rabbit Lude\'s Hard', 'audio.mp3', 42005, 'haloween.jpg', NULL, 1708028368),
(33, '14', 3917272, -3917272, 1900394, '64ce780a48fe717ab454008452d78fec', 'katagiri - STRONG 280 (mokumoku-) [TURBULENT~!].osu', 'katagiri', 'STRONG 280', 'mokumoku-', 'TURBULENT~!', 'audio.mp3', 212518, '1228547.jpg', NULL, 1708028371);

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
  ADD KEY `file_name` (`file_name`(768)) USING BTREE;

--
-- 덤프된 테이블의 AUTO_INCREMENT
--

--
-- 테이블의 AUTO_INCREMENT `beatmapsinfo`
--
ALTER TABLE `beatmapsinfo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
