#NoEnv
; #Warn ; 不显示警告窗口
SendMode Input
SetWorkingDir %A_ScriptDir% ; 当前工作目录

#Include loadgame.ahk
#Include tracker.ahk

; ----------------------------------------------------------------
; 一字不落游戏，无限模式特殊字根下运行
; 按热键CTRL+J运行
; 游戏内界面坐标(678~1220, 10~950)
; TODO: MsgBox改为在cmd窗口显示提示
; ----------------------------------------------------------------

AutoInf()
{
	SetKeyDelay 0, 10 ; 设置按下延时(PressDuration)为10
	
	; 游戏目录: 根据自己exe文件所在位置更改
	gamePath := "D:\Steam\steamapps\common\一字不落\Chinatris.exe"
	isGameOpened := true ; 是否已打开游戏
	isInLevel := true ; 不需要加载
	
	; 进入游戏界面A
	if (not isInLevel)
		EnterInfMode(gamePath, isGameOpened)
	
	; 恢复初始状态
	FileCopy make_move\test\初始状态.txt, make_move\当前状态.txt, true
	
	; <检测，然后MsgBox 检测到成功进入游戏。>
	Send D ; 首字右移
	Send {S down}
	Sleep 400
	Send {S up}
	
	firstUnknown := true ; 还未检测首字
	
	; 获取首个下一字
	now := "" ; 当前字已在下落
	next := GetNextZi()
	
	; 首轮初始化、获取目标
	made_moves := 0
	count := 4
	targetToChange := false
	targets := GetTargets()
	targetStr := getArrayAsStr(targets)
	
	; 测试Targets
	
	; MsgBox 第一题检测到的目标字:%targetStr%
	
	Loop ; 主循环
	{
		; <可设置时间/检测题数退出>
		made_moves := made_moves + 1
		if made_moves > 100
		{
			MsgBox 100步测试完成，即将退出。
			Exit
		}
		
		Loop ; 落字检测循环
		{
			if IsNewFall()
			{
				; MsgBox 检测到新的落字。
				
				; 更新当前字、下一字、计数
				now := next
				next := GetNextZi()
				; MsgBox 检测到当前字'%now%'，预告字'%next%'。
				
				Sleep 160 ; 由于数字改变的动画有延迟，需隔一小会再检测新值
				newCount := GetCount()
				while(newCount = "" or newCount = 0) 
				{
					if (newCount = 0)
					{
						targetToChange := true ; 将出现新题
					}
					Sleep 40 ; 正在变动，稳定后再次检测
					newCount := GetCount()
				}
				
				if (newCount > count or targetToChange)
				{
					MsgBox 检测到新的题目，由于检测题字缺漏需检测消字区的逻辑还没写完。
					targets := GetTargets()
					targetStr := getArrayAsStr(targets)
					targetToChange := false
					; ReloadZi() ; 重新载入消字区, 每次载入1格暂未确定如何载入
					; 暂未记录过题数并写入
				}
				if (newCount < count)
				{
					; MsgBox 检测到成功消除，计数由'%count%'降至'%newCount%'。
				}
				count := newCount
				break
			}
			Sleep 100 ; 未检测到时，每0.1秒检测1次
		}
		
		; 首字处理(刚开始游戏时)
		if firstUnknown
		{
			firstzi := GetRightCornerZi()
			firstUnknown := false
			ReloadZi(9, 4) ; 首字已稳定,可检测(由于初始右移,在(9, 4))
		}
		
		; 根据处理逻辑计算下一步
		moveInfo := ExtLogic(now, next, count, targetStr)
		moveTime := 0
		SendMoves(moveInfo[1]) ; 信息[1]: 当前move
		
		; 加速下落至列顶(4+格时)
		if (moveInfo[2] >= 4)
		{
			moveTime := moveInfo[2]*50
			Send {S down}
			Sleep %moveTime% ; 每0.1s大约1.0~1.4格,有加速度
			Send {S up}
			KeyWait S
		}
		
		; 防止新落字时检测过快1次变为多次
		if (moveTime < 420)
		{
			SleepTime := 500 - moveTime ; 
			Sleep %SleepTime% ; 补加速下落的Sleep时间
		}
	}

	return
}

^j::AutoInf()

^Enter::Reload
^Space::Pause
