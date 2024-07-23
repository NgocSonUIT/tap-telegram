const WebSocket = require('ws')
const wsUrl =
  'wss://tg.dev.treasuretapper.xyz/socket.io/?EIO=4&transport=websocket'
const headers = {
  'User-Agent':
    'Mozilla/5.0 (Linux; Android 10; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0'
}
const ws = new WebSocket(wsUrl, { headers })
let userScore = 0
let isUserIdSent = false
let isGameDataMessageSent = false

ws.on('open', function open() {
  console.log('Kết nối WebSocket')
  const data = { userId: '1131067314' }
  const message = `40${JSON.stringify(data)}`
  ws.send(message)
  isUserIdSent = true
})

ws.on('message', function incoming(data) {
  const message = data.toString()
  console.log('Nhận tin nhắn từ server:', message)
  if (
    isUserIdSent &&
    !isGameDataMessageSent &&
    message.includes('42["SOCKET_READY"')
  ) {
    const gameDataMessage = `42["GET_GAME_DATA", "{}"]`
    ws.send(gameDataMessage)
    console.log('Lấy dữ liệu:', gameDataMessage)
    isGameDataMessageSent = true
  }
  if (message.startsWith('42["GET_GAME_DATA"')) {
    const parsedMessage = JSON.parse(message.slice(2))
    const gameData = JSON.parse(parsedMessage[1])
    const lastGain = gameData.data.last_gain
    userScore = lastGain + 1
    const setUserDataPayload = {
      userScore: userScore,
      pointPerTap: 1,
      click: 1
    }
    const setUserDataMessage = `42["SET_USER_DATA", ${JSON.stringify(
      setUserDataPayload
    )}]`
    ws.send(setUserDataMessage)
    console.log('Bắt đầu tap:', setUserDataMessage)
  }

  userScore += 1
  const setUserDataPayload = {
    userScore: userScore,
    pointPerTap: 1,
    click: 1
  }
  const setUserDataMessage = `42["SET_USER_DATA", ${JSON.stringify(
    setUserDataPayload
  )}]`
  ws.send(setUserDataMessage)
  console.log('Bắt đầu tap:', setUserDataMessage)
})

ws.on('close', function close() {
  console.log('Ngắt kết nối WebSocket')
})

ws.on('error', function error(err) {
  console.error('Lỗi rồi:', err)
})
