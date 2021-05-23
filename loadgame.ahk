#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir% ; 当前工作目录


EnterInfMode(gamePath, isGameOpened)
{
	; 运行游戏
	if not isGameOpened
	{
		Run %gamePath%
		Sleep 18000 ; 等待游戏加载 <18s
	}

	; 游戏外界面: 无限(1024, 876) 退出(1024, 986) 无限开始(1472,760) 无限返回(1850,1016)
	Click 1024, 876 ;进入无限模式
	Sleep 1800 ; 加载动画=1.6s

	; 游戏内界面：按ESC/Click (728, 40) 继续(374,720) 重玩(374,840) 退出(960)
	Click 1472, 760
	Sleep 3700 ; 加载动画~=2.0s, 能看见移动的时间<3.7s
	
	MouseMove 1750, 850 ; 移开笔避免影响检测
	Sleep 500
}
