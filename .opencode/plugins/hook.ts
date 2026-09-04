import type { PluginInput, PluginOptions, Hooks } from "@opencode-ai/plugin"

// v1.1.0: 中英双语 + 变体；仅用于提示横幅，真正路由由 opencode.json agent/skills 决定
const RED_FLAGS = [
  "洗钱", "诈骗", "挪用", "舞弊", "恐怖融资", "制裁", "黑名单", "涉案", "冻结",
  "造假", "财务造假", "资金占用", "关联方占用", "平仓", "质押爆仓", "审计保留",
  "money laundering", "fraud", "embezzle", "misappropriation", "terrorist financing",
  "sanction", "blacklist", "margin call", "pledge liquidation", "qualified opinion",
  "restatement", "short seller", "做空",
]

const bashTimers = new Map<string, number>()

// 只读安全命令：自动放行，减少 HITL 轰炸
const READONLY_ALLOW = /^\s*(ls|cat|head|tail|wc|find|grep|awk|sort|uniq|cut|tr|column)(\s|$)/

export default async (
  _input: PluginInput,
  _options?: PluginOptions,
): Promise<Hooks> => {
  return {
    async "chat.message"(_input, output) {
      const parts = output.parts as Array<{ type: string; text?: string }>
      const text = parts
        .filter((p) => p.type === "text")
        .map((p) => p.text ?? "")
        .join(" ")

      const lower = text.toLowerCase()
      const matched = RED_FLAGS.some((f) => lower.includes(f.toLowerCase()))
      if (matched) {
        const prefix = "[🔍 查黑账 Agent 已接管]\n"
        output.parts = [
          { type: "text", text: prefix },
          ...parts,
        ] as any
      }
    },

    async "tool.execute.before"(input, output) {
      if (input.tool === "bash") {
        const args = output.args as Record<string, unknown>
        const command = (args?.command as string) ?? ""

        bashTimers.set(input.callID, Date.now())

        const dangerousPatterns = [
          /\brm\s+.*-[a-z]*r[a-z]*f\b/, // rm -rf 变体
          /\brm\s+.*\s+\/\s*($|;|&&)/, // rm ... /
          /\brm\s+.*~(\s|$)/, // rm ~ 误删家目录
          /\bdd\b.*\bof=\/dev\//,
          /\bmkfs\b/,
          /\bshutdown\b|\breboot\b|\bhalt\b|\bpoweroff\b/,
          /:\(\)\s*\{\s*:\|\:&\s*\};:/, // fork bomb
          /\bchmod\s+(-R\s+)?777\b/,
          /\bchown\s+-R\b/,
          /\bwget\b/,
          /\bcurl\b/, // 默认拦截 curl，外发需走白名单 HITL； финансовый 研究抓取请用 webfetch 工具而非 bash curl
          /\b(curl|wget)\b.*\|\s*(sh|bash)\b/, // v1.2.0: 管道到 shell 一律拦截 (投毒经典向量)
          /\bpython3?\b.*\bos\.system\b/,
          /\bpython3?\b.*\bsubprocess\b/,
          /\bpython3?\b.*\bsocket\b/,
          /\bpython3?\b.*\brequests\b/,
          /\bpython3?\b.*\bakshare\b/,
          /\bpython3?\b.*\byfinance\b/,
          /\bos\.environ\b/,
          /\bprintenv\b/,
          // env 单独出现才拦，避免误杀 environment 等正常词
          /(^|[\s;&|])env(\s|$)/,
          />\s*\/dev\//,
          /\bgit\s+push\s+.*--force\b/,
          /\bnc\s+-l\b/,
          /\bbase64\s+(-d|--decode)\b.*\|\s*(sh|bash)\b/,
        ]

        for (const pattern of dangerousPatterns) {
          if (pattern.test(command)) {
            throw new Error(
              `[🛡️ 黑账审计安全钩子] 阻止危险命令模式: ${pattern.source} 在命令中检测到: ${command.slice(0, 300)}`
            )
          }
        }
      }
    },

    async "tool.execute.after"(input, output) {
      if (input.tool === "bash") {
        const start = bashTimers.get(input.callID)
        if (start) {
          const duration = Date.now() - start
          bashTimers.delete(input.callID)
          if (duration > 30000) {
            console.log(`[⏱️ 黑账审计] Bash 执行耗时 ${duration}ms，可能涉及大规模数据处理`)
          }
        }
      }
    },

    async "shell.env"(_input, output) {
      output.env["BLACK_ACCOUNT_AUDIT"] = "1"
      output.env["AUDIT_MODE"] = "strict"
      // v1.1.0: 修正大小写笔误，大小写双写兼容旧引用
      output.env["FINANCIAL_AUDIT_MODE"] = "strict"
      output.env["FINANCIAL_AUDIT_mode"] = "strict"
    },

    async "permission.ask"(input, output) {
      // v1.1.0: 分级放行，解决“恒 ask 卡死流水线”
      try {
        const tool = (input as any)?.tool ?? (input as any)?.toolName ?? ""
        const args = (output as any)?.args as Record<string, unknown> | undefined
        const command = (args?.["command"] as string) ?? ""
        if (tool === "bash" && READONLY_ALLOW.test(command)) {
          ;(output as any).status = "allow"
          return
        }
      } catch {
        // 解析失败则回退到 ask
      }
      ;(output as any).status = "ask"
    },
  }
}
