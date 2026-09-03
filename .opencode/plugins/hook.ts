import type { PluginInput, PluginOptions, Hooks } from "@opencode-ai/plugin"

const RED_FLAGS = ["洗钱", "诈骗", "挪用", "舞弊", "恐怖融资", "制裁", "黑名单", "涉案", "冻结"]

const bashTimers = new Map<string, number>()

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
        const prefix = "[🔍 查黑账 Agent 已接管]\\n"
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
          /\\brm\\s+-(rf|fr)\\b/,
          /\\bmkfs\\b/,
          /\\bchmod\\s+777\\b/,
          />\\s*\\/dev\\//,
          /\\bwget\\b/,
          /\\bcurl\\s+-X\\s+DELETE\\b/
        ]

        for (const pattern of dangerousPatterns) {
          if (pattern.test(command)) {
            throw new Error(`[🛡️ 黑账审计安全钩子] 阻止危险命令模式: ${pattern.source} 在命令中检测到: ${command}`)
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
      output.env["FINANCIAL_AUDIT_mode"] = "strict"
    },

    async "permission.ask"(_input, output) {
      output.status = "ask"
    },
  }
}