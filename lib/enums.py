class RegisterError:
  """
  Success = "1"

  GenericError = "-1"

  AccountExists = "-2"
  EmailIsInUse = "-3"

  InvalidUserName = "-4"
  InvalidPassword = "-5"
  InvalidEmail = "-6"

  PasswordIsTooShort = "-8"
  UserNameIsTooShort = "-9"

  PasswordsDoNotMatch = "-7"
  EmailsDoNotMatch = "-99"
  """
  Success = "1"
  GenericError = "-1"
  AccountExists = "-2"
  EmailIsInUse = "-3"
  InvalidUserName = "-4"
  InvalidPassword = "-5"
  InvalidEmail = "-6"
  PasswordIsTooShort = "-8"
  UserNameIsTooShort = "-9"
  PasswordsDoNotMatch = "-7"
  EmailsDoNotMatch = "-99"


class LoginError:
  """
  GenericError = "-1"
  WrongCredentials = "-11"

  AlreadyLinkedToDifferentAccount = "-10"

  PasswordIsTooShort = "-8"
  UserNameIsTooShort = "-9"

  AccountIsBanned = "-12"
  AccountIsNotActivated = "-13"
  """
  GenericError = "-1"
  WrongCredentials = "-11"
  AlreadyLinkedToDifferentAccount = "-10"
  PasswordIsTooShort = "-8"
  UserNameIsTooShort = "-9"
  AccountIsBanned = "-12"
  AccountIsNotActivated = "-13"


class BackupError:
  """
  GenericError = "-1"

  WrongCredentials = "-2"
  BadLoginInfo = "-5"

  TooLarge = "-4"
  SomethingWentWrong = "-6"
  """
  GenericError = "-1"
  WrongCredentials = "-2"
  BadLoginInfo = "-5"
  TooLarge = "-4"
  SomethingWentWrong = "-6"


class CommonError:
  """
  Success = "1"

  InvalidRequest = "-1"
  SubmitRestoreInfo = "-9"

  Banned = "-10"
  Disabled = "-2"

  Filter = "-15"
  Automod = "-16"
  """
  Success = "1"
  InvalidRequest = "-1"
  SubmitRestoreInfo = "-9"
  Banned = "-10"
  Disabled = "-2"
  Filter = "-15"
  Automod = "-16"


class LevelUploadError:
  """
  Success = "1"

  UploadingDisabled = "-2"
  TooFast = "-3"

  FailedToWriteLevel = "-5"
  """
  Success = "1"
  UploadingDisabled = "-2"
  TooFast = "-3"
  FailedToWriteLevel = "-5"


class CommentsError:
  """
  NothingFound = "-2"
  """
  NothingFound = "-2"


class Action:  # Last action ID is 56
  AccountRegister = 1
  UserCreate = 51

  SuccessfulLogin = 2
  FailedLogin = 6

  # To be done with dashboard
  SuccessfulAccountActivation = 3
  FailedAccountActivation = 4

  SuccessfulAccountBackup = 5
  FailedAccountBackup = 7

  LevelUpload = 22
  LevelChange = 23
  LevelDeletion = 8

  ProfileStatsChange = 9
  ProfileSettingsChange = 27
  UsernameChange = 49
  PasswordChange = 50

  SuccessfulAccountSync = 10
  FailedAccountSync = 11

  AccountCommentUpload = 14
  AccountCommentDeletion = 12

  CommentUpload = 15
  CommentDeletion = 13

  ListUpload = 17
  ListChange = 18
  ListDeletion = 19

  DiscordLink = 24
  DiscordUnlink = 25
  DiscordLinkStart = 26
  FailedDiscordLinkStart = 47
  FailedDiscordLink = 48

  FriendRequestAccept = 28
  FriendRequestDeny = 30
  FriendRemove = 31
  FriendRequestSend = 33

  BlockAccount = 29
  UnblockAccount = 32

  LevelScoreSubmit = 34
  LevelScoreUpdate = 35

  PlatformerLevelScoreSubmit = 36
  PlatformerLevelScoreUpdate = 37

  VaultCodeUse = 38

  CronAutoban = 39
  CronCreatorPoints = 40
  CronUsernames = 41
  CronFriendsCount = 42
  CronMisc = 43
  CronSongsUsage = 44

  LevelVoteNormal = 45
  LevelVoteDemon = 46

  GlobalLevelUploadRateLimit = 52
  PerUserLevelUploadRateLimit = 53
  AccountRegisterRateLimit = 54
  UserCreateRateLimit = 55
  FilterRateLimit = 56

  # Unused
  GJPSessionGrant = 16
  LevelReport = 20
  LevelDescriptionChange = 21


class ModeratorAction:  # Last action ID is 46
  LevelRate = 1
  LevelDailySet = 5
  LevelDeletion = 6
  LevelCreatorChange = 7
  LevelRename = 8
  LevelPasswordChange = 9
  LevelCreatorPointsShare = 11
  LevelPrivacyChange = 12
  LevelDescriptionChange = 13
  LevelChangeSong = 16
  LevelLockUpdating = 29
  LevelLockCommenting = 38
  LevelSuggest = 41
  LevelEventSet = 44
  LevelScoreDelete = 45

  PersonBan = 28
  PersonUnban = 46

  # To be done with dashboard
  LevelSuggestRemove = 40
  MapPackCreate = 17
  GauntletCreate = 18
  SongChange = 19
  ModeratorPromote = 20
  MapPackChange = 21
  GauntletChange = 22
  QuestChange = 23
  ModeratorRoleChange = 24
  QuestCreate = 25
  AccountCredentialsChange = 26
  SFXChange = 27
  VaultCodeCreate = 42
  VaultCodeChange = 43

  ListRate = 30
  ListSuggest = 31
  ListPrivacyChange = 33
  ListDeletion = 34
  ListCreatorChange = 35
  ListRename = 36
  ListDescriptionChange = 37
  ListLockCommenting = 39

  # Unused
  LevelFeature = 2
  LevelCoinsVerify = 3
  LevelEpic = 4
  LevelDemonChange = 10
  LevelToggleLDM = 14
  LeaderboardsBan = 15
  ListFeature = 32


class Color:
  Blue = "b"
  Green = "g"
  LightBlue = "l"
  JeansBlue = "j"
  Yellow = "y"
  Orange = "o"
  Red = "r"
  Purple = "p"
  Violet = "a"
  Pink = "d"
  LightYellow = "c"
  SkyBlue = "f"
  Gold = "s"
  Undefined = ""

class Permission:
  commandRate = "commandRate"
  commandFeature = "commandFeature"
  commandEpic = "commandEpic"
  commandUnepic = "commandUnepic"
  commandVerifycoins = "commandVerifycoins"
  commandDaily = "commandDaily"
  commandWeekly = "commandWeekly"
  commandDelete = "commandDelete"
  commandSetacc = "commandSetacc"
  commandRenameOwn = "commandRenameOwn"
  commandRenameAll = "commandRenameAll"
  commandPassOwn = "commandPassOwn"
  commandPassAll = "commandPassAll"
  commandDescriptionOwn = "commandDescriptionOwn"
  commandDescriptionAll = "commandDescriptionAll"
  commandPublicOwn = "commandPublicOwn"
  commandPublicAll = "commandPublicAll"
  commandUnlistOwn = "commandUnlistOwn"
  commandUnlistAll = "commandUnlistAll"
  commandSharecpOwn = "commandSharecpOwn"
  commandSharecpAll = "commandSharecpAll"
  commandSongOwn = "commandSongOwn"
  commandSongAll = "commandSongAll"
  profilecommandDiscord = "profilecommandDiscord"
  actionRateDemon = "actionRateDemon"
  actionRateStars = "actionRateStars"
  actionRateDifficulty = "actionRateDifficulty"
  actionRequestMod = "actionRequestMod"
  actionSuggestRating = "actionSuggestRating"
  actionDeleteComment = "actionDeleteComment"
  toolLeaderboardsban = "toolLeaderboardsban"
  toolPackcreate = "toolPackcreate"
  toolQuestsCreate = "toolQuestsCreate"
  toolModactions = "toolModactions"
  toolSuggestlist = "toolSuggestlist"
  dashboardModTools = "dashboardModTools"
  modipCategory = "modipCategory"
