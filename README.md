# uart_draw 即時 ADC 波形監看工具

> **Python + Matplotlib** 製作的即時 UART 資料視覺化程式  
> 支援移動平均濾波、一階微分與 4 視窗同步捲動

---

## 目錄

1. [專案簡介](#專案簡介)
2. [功能](#功能)
3. [專案結構](#專案結構)
4. [環境需求](#環境需求)
5. [主要參數](#主要參數)
6. [開發指南](#開發指南)
7. [授權](#授權)

---

## 專案簡介

本工具用來即時監看 MCU 透過 **UART** 傳出的 ADC 取樣值 (預設 1k S/s), 此數值與 MCU 傳送值有關 ：

1. **接收** – 背景執行緒持續監聽序列埠並寫入環形緩衝區
2. **處理** – 套用移動平均濾波並計算一階微分
3. **繪圖** – 每 40 ms 更新以下 4 幅波形
    * 原始 ADC 值
    * 原始值微分
    * 濾波後 ADC 值
    * 濾波後值微分

所有圖表自動維持 5 s 觀測窗並平滑捲動。

---

## 功能

| 功能        | 說明                                                       |
|-----------|----------------------------------------------------------|
| 多執行緒架構    | UART 讀取與 GUI 分離                                          |
| 可配置通訊參數   | `PORT`、`BAUD_RATE`、`SYNC_BIT` 可分別設定調整                    |
| 13-bit 解析 | 0xAA 同步碼 → 2 Byte Little Endian → `& 0x0FFF` 取得 0 – 4095 |
| 移動平均濾波    | 預設 5 點；修改 `model.WINDOW_SIZE` 可調整                        |
| 一階微分      | 以 `np.gradient()` 中央差分，長度與原始資料相同                         |

---

## 專案結構

```text
uart-draw/
├── reader.py      # UART 讀取執行緒
├── model.py       # ADCData 類別與濾波器
├── plotting.py    # Matplotlib 動畫邏輯
├── main.py        # 程式進入點
├── pyproject.toml # 相依套件定義
└── uv.lock        # （可選）uv 產生的鎖檔
```

---

## 環境需求

本專案使用 **Python 3.8+** 開發，並使用 **uv** 套件來管理相依性。

理論上在任何支援 Python 的作業系統上都能運行，但目前只在 **Linux** 上測試過。

---

## 主要參數

| 參數               | 位置          | 預設值            | 說明                 |
|------------------|-------------|----------------|--------------------|
| `PORT`           | `reader.py` | `/dev/ttyACM0` | 串列埠名稱              |
| `BAUD_RATE`      | `reader.py` | `115200`       | 鮑率                 |
| `SYNC_BIT`       | `reader.py` | `0xAA`         | 資料同步起始位元           |
| `SAMPLE_RATE`    | `model.py`  | `1000`         | MCU 取樣頻率 (Hz)      |
| `WINDOW_SECONDS` | `model.py`  | `5`            | 圖形顯示時窗 (s)         |
| `WINDOW_SIZE`    | `model.py`  | `5`            | 移動平均窗口長度 (samples) |

## 開發指南

### 執行步驟

1. 確保已安裝 **Python 3.8+** 和 **uv** 套件
2. 在專案目錄下執行 `uv run` 以安裝相依套件
3. 修改 `reader.py` 中的 `PORT`、`BAUD_RATE` 和 `SYNC_BIT` 參數
4. 執行 `uv run main.py` 開始程式

### Commit 規範

採用 [Conventional Commits](https://www.conventionalcommits.org/zh-hant/v1.0.0/)，如下範例：

```bash
git commit -m "feat(model): add Butterworth filter helper"
```





