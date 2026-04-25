-- 监视生命值 + 体力，并写入日志文件

-- 使用正斜杠，避免转义问题
local logFilePath = "health_stamina_status.json"

local function writeToFile(filename, content)
    local file, err = io.open(filename, "a")
    if file then
        file:write(content .. "\n")
        file:close()
        return true
    else
        print("写入文件失败: " .. tostring(err))
        return false
    end
end

local function getHealthAndStamina()
    local statPools = Game.GetStatPoolsSystem()
    local player = Game.GetPlayer()
    if not statPools or not player then
        return nil, nil
    end
    local playerID = player:GetEntityID()
    local health = statPools:GetStatPoolValue(playerID, gamedataStatPoolType.Health)
    local stamina = statPools:GetStatPoolValue(playerID, gamedataStatPoolType.Stamina)
    return health, stamina
end

local function logValues()
    local hp, stam = getHealthAndStamina()
    if hp and stam then
        local timestamp = os.date("%Y-%m-%d %H:%M:%S")
        local line = string.format("[%s] Health: %.3f, Stamina: %.3f", timestamp, hp, stam)
        print(line)
        writeToFile(logFilePath, line)
    else
        local errLine = string.format("[%s] Failed to get values (player not ready)", os.date("%Y-%m-%d %H:%M:%S"))
        print(errLine)
        writeToFile(logFilePath, errLine)
    end
end

local elapsed = 0
local interval = 0.05

registerForEvent("onUpdate", function(deltaTime)
    elapsed = elapsed + deltaTime
    if elapsed >= interval then
        elapsed = 0
        logValues()
    end
end)

registerForEvent("onInit", function()
    print("✅ 生命值+体力监视模组已加载，每秒记录到文件")
    Game.ShowNotification("✅ 状态日志记录已启动")
    logValues()
end)
