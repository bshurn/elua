-- LPCXPresso BaseBoard build configuration

return {
  cpu = 'lpc1769',
  components = {
    romfs = true,
	wofs = false,
	shell = true,
	advanced_shell = false,
	sercon = { uart = 0, speed = 115200, timer=systimer, flow=none, buf_size=32 },        
    xmodem = true,
	term = false,
	cints = false,
	luaints = false,
	tcip = false,
	dns = false,
	dhcp = false,
	tcpipcon = false,
    linenoise = { shell_lines = 10, lua_lines = 50 },
	rfc = false,
	mmcfs = false,
    rpc = false,
	sermux = false,
    adc = false,
	lpc17xx_semifs = false
  },
  config = {
	vtmr = false,
    egc = { mode = "disable" },
    ram = { internal_rams = 1 }
  },
  modules = {
    generic = { 'all_lua', 'elua', 'pd', 'pio', 'term', 'tmr', 'uart'},
    platform = 'all'
  }
}

