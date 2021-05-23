#NoEnv
; #Warn ; 不显示警告窗口
SendMode Input
SetWorkingDir %A_ScriptDir% ; 当前工作目录

getArrayAsStr(array)
{
	str := ""
	for i, x in array
	{
		 str = %str%%x%,
	}
	StringTrimRight str, str, 1
	return str
}

SearchZi(matchPath, sx, sy, ex, ey)
{
	Loop %matchPath%
	{
		ImageSearch, retx, rety, sx, sy, ex, ey, *2 %A_LoopFileFullPath%
		if ErrorLevel = 0
		{
			Name := A_LoopFileName
			StringReplace Name, Name, .bmp, , All
			return Name ; 匹配成功，返回匹配的图片名
		}
	}
	return "" ;
}

GetNextZi() ; 获取下一个字
{
	; 预告区(690~1220, 80~180)
	return SearchZi("src\next\*.bmp", 690, 80, 790, 180)
}

IsNewFall() ; 匹配出现落字的特征
{
	; 落字区(808~1128,178~248)
	fall := SearchZi("src\fall\*.bmp", 808, 178, 1128, 248)
	return (fall <> "")
}

GetRightCornerZi() ; 获取右下角(首字)
{
	; 右下角(首字)区(1041~1109,871~938)
	return SearchZi("src\word\*.bmp", 1041, 871, 1109, 938)
}

GetCount() ; 获取剩余计数
{
	; 计数区(800~840,140~180)
	return SearchZi("src\count\*.bmp", 800, 140, 840, 180)
}

GetTargets() ; 返回目标数组
{
	; 目标区(837~1200, 106~164)
	Array := Object()

	matchPath := "src\target\*.bmp"
	Loop %matchPath%
	{
		ImageSearch, retx, rety, 837, 106, 1200, 164, *160 *TransBlack %A_LoopFileFullPath%
		if ErrorLevel = 0
		{
			Name := A_LoopFileName
			StringReplace Name, Name, .bmp, , All
			Array.Insert(Name) ; 匹配成功，放入数组
		}
	}
	return Array
}

; <从游戏中途继续> 其他区域: 消词区(730~1200, 170~950)

ExtLogic(zi_a, zi_b, cnt, targetStr)
{
	; MsgBox 传入参数：-a %zi_a% -b %zi_b% -c %cnt% -t %targetStr%。
	pyPath := "calc.py"
	workDir := "make_move"
	
	Run Cmd /k "Python %pyPath% -a %zi_a% -b %zi_b% -c %cnt% -t %targetStr%", %workDir%, hide
	Sleep 120 ; python run ~= 0.02s < 0.12s
	WinKill Cmd
	
	FileRead outputStr, %workDir%\move.txt ; 结果为[-2,1]的数
	moveInfo := StrSplit(outputStr, ",")
	FileDelete %workDir%\move.txt
	t1 := moveInfo[1]
	t2 := moveInfo[2]
	; MsgBox 返回参数:[%t1%,%t2%]。
	
	return moveInfo
}

SendMoves(ID)
{
	if ID = -2
	{
		Send A
		Sleep 5
		Send A
		KeyWait A
	}
	else if ID = -1
	{
		Send A
		KeyWait A
	}
	else if ID = 1
	{
		Send D
		KeyWait D
	}
	
	return
}


ReloadZi(row, col) ; row从上往下取值[1,9], col从左往右取值[1,4]
{
	; 由于太慢(每次循环0.x sec(s)),现在还用不了
	; 可行方法: 等字下落时更新非下落列的,每次更新1格(可改为python调用ahk.dll)
	
	posID := row + (col - 1)*9
	isLastRow := (posID - posID//9*9) = 0
	id := posID - 1
	sx := 811 + id//9*77
	sy := 254 + (id - id//9*9)*77
	
	zi := ""
	matchPath := "src\zi\*.bmp"
	Loop %matchPath%
	{
		ImageSearch, retx, rety, sx, sy+isLastRow
			, sx+66, sy+67-isLastRow, *160 *TransBlack %A_LoopFileFullPath%
		if ErrorLevel = 0
		{
			; 空字'.'的检测由于有渐变背景还未截图和写
			zi := A_LoopFileName
			StringReplace zi, zi, .bmp, , All
			break
		}
	}
	if zi == "" ; 未检测确定
		return
	; MsgBox 当前在循环次数%A_Index%。
	
	pyPath := "calc.py"
	workDir := "make_move"
	
	ziInfo := Object()
	ziInfo.Insert(zi)
	ziInfo.Insert(row-1)
	ziInfo.Insert(col-1)
	ziInfoStr := getArrayAsStr(ziInfo)
	
	; MsgBox 1格字检测.传入参数-s %ziInfoStr%。
	Run Cmd /k "Python %pyPath% -s %ziInfoStr%", %workDir%, hide
	
	return
}
