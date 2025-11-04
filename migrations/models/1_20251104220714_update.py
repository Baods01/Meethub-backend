from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `roles` ADD `permissions` JSON COMMENT '权限列表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `roles` DROP COLUMN `permissions`;"""


MODELS_STATE = (
    "eJztmutP4zgQwP+Vqp84iVulafPgvpXH3fYE9ATlbrXLKnISp41InG7iANWK//3GzvtVEi"
    "i0C3yJUnsmsX8ztmem+dl3PRM7waerAPtB/4/ezz5BLoabYsd+r4+Wy6yZNVCkO1wyTEX0"
    "gPrIoNBoISfA0GTiwPDtJbU9wkSvQ0US1etQFofKdaiqssr0TM8ARZvMqyIyEgfXoaSoOh"
    "MMif0jxBr15pgusA/i375Ds01MfI+D5OfyRrNs7JiF6dgmewBv1+hqydsmhP7JBdkYdM3w"
    "nNAlmfByRRceSaVtQlnrHBPsI4rZ46kfskmS0HFiGMm8o5FmItEQczomtlDoMFRMez2pyX"
    "GZUqxjeIQRh5FFtpuzN/4uDkbKSB3KIxVE+KjSFuUhmmrGIVLkNM5n/QfejyiKJDjSjCEz"
    "NL+vkDxaIL8eZV6nBBSGXgaa4HtpouBSI8FsSdVF95qDyZwu4KckrEH47/ji6PP4Yk8Sfm"
    "PP9mAxREvkPO4ReRejnFFdoiC48/wa/2ymmtfZDNWkIcOaLeHHuEq6IQNdVRg8hehAVFsg"
    "BalGpryvCBW7yHa6EE0VnoQzdsEN+OiBgDCw1PUnsRQlqQVLkGpkyftKDgo8Oq35VGHLLG"
    "VxpMNVGSLw0aGlPMk7B22cc9Dsm4MyTnQL+6vfhWemsRGgz1rqB8MRXAXDuro43RkPJbZx"
    "0/VgyutsHassDyVY9QeWsBtnkm57VZYzfN8QL8XiW8c4wiJiVx2xLVQV2L2ht0O6BuHs5M"
    "uMPcQNgh9OHt3e2fgLp+qu4p7T6flfiXgO9dHp9LCE2A40CJXt2xqnPfQ8ByPSEJvm9UrE"
    "dVB8qcM/3XUrritaLJwSIQSQLQOYy+bw+cwPp9PTAvPDSRnq1dnhCey93AAgZNMoqI/D2A"
    "LpW+zb8JaaGOsx1nnNV6TdmD/lcR8g1YAsSjdaxgqvg9vwMYOhIVqlfQw91HZxPe6iZom2"
    "Gat+Sm5ePcoVBxBNSCAHVpAsxl+yRi33a5iZOSXOKl5I6zabydnJ5Wx89k/BHMfj2QnrEQ"
    "u7TdK6J5f29vQhvf8ms8899rP3dXp+wrl6AZ37/I2Z3Oxrn40JhdTTiHenITMXaSWtCa6C"
    "ucOl+URzFzV3zdyybI2YoXXhHZs7HnxmbQcFVHO8uU26WruouQFrbzT+UgSB1wRY7iUrbJ"
    "1bktTd8L+IoRMwlYXNymfWTa74wxp0ZNzcId/UKj2e6DXJVrtc0a2tKvlwAAdVbzpDZDXz"
    "2JX70wQ4I2LURT1xpfIiec52CkrqgSnCVVTETq6StWYv5hPSSoXYdHo+dvi2ma/KRfw8n6"
    "O/wauUqxaVMlOzxH1cJ+6jC98L54ukWUvtAYjhzTg654/Gl0fjY+5oWgUw9xsXETTnbWzC"
    "D/ulkdfUltMpNdeW08G0qS1nJmisLedF3nFtOcOwK7Xlzun7jtSU8w7Fasq7lMUbsJ66ME"
    "3kd4mpYg2eUVvePNP8YCtomyskJbWtV0oK++DQgJRStdq67Uel5K1WSj5S95oN5a3kch+p"
    "+7sydyV1X2LftYMAKNVkW39fTs8b/swrqpVsfUWg45tpG3S/59gB/f7qiftoCOaVJYGv8o"
    "aPSjrvqQzH+nOsfGSVzMUewM6xbSTUWUL4vIQ6/fTnbSbU6fTKCXVWkCgm1PmkuZxQ55Pt"
    "5yXUfN2uzafH2LeNRb8moY579tdl1CiTeSylTqxURf9+kuVmBq+cIN+C89UmHc35XE5lyx"
    "8Jtaf48h8LsKXRAWIs/msCHAhtEmCQav5+RagpKxCKSU3M2BxE5FQ2EEBsAevbihVqjpeH"
    "/wGGvvfN"
)
