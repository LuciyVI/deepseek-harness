# 在聊天中运行 Harness²

[English](harness2.md) | 中文

此可选集成向 dsh 聊天添加 `/harness2 on|off|status`。启用后，每个新的文本任务先在项目副本中执行完整的 Harness² 适配循环，然后 dsh 接收选定的回复、修改和 harness。新聊天默认关闭此模式。

## 安装

使用此 fork 的 `feat/harness2-integration` 分支、Node 24、Python 3.12 或 3.13，以及已经配置模型的 dsh 0.2.0-rc.2。此示例尚未验证其他 dsh 版本。在本仓库中运行：

```sh
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install 'harness2 @ git+https://github.com/LuciyVI/harness2.git@dsh-integration-v6'
python apps/cli/config/examples/harness2/install.py --profile web
```

配套 fork 提供 Python 执行器和适配引擎。如果 `PATH` 中没有 `dsh`，请在安装前将 `HARNESS2_DSH_COMMAND` 设置为已安装的启动器，例如 `node /absolute/path/to/dsh/lib/bin.js`。安装器定位该运行时的依赖，在现有配置补丁中添加带标记的配置块，并创建私有备份；它不会修改 npm 运行时或模型提供方配置。

通过平常的 profile 启动方式重启 dsh，并选择具有 `workspace-write` 权限的项目工作区。模型和搜索端点必须已经可达。

## 使用

在聊天中发送一条命令：

```text
/harness2 on
/harness2 status
/harness2 off
```

选择仅属于当前聊天，并从已记录的命令事件恢复。命令本身不调用模型。启用模式后，任务依次执行基线、harness 修改与试运行、组合、最终执行和经验反思。默认 `k=1` 时，直接采用唯一的组合结果，不执行比较调用；完成循环并不代表质量提升。

试运行不会修改原始项目。普通 dsh 代理接收选定的产物，检查内容，并使用正常工具应用任务要求的项目修改。关闭模式会取消当前循环并禁用后续循环；插件卸载会等待其 worker 结束。求解和改进子会话不能启动嵌套的适配循环。

## 限制与恢复

每个模型会话的默认时限为 3600 秒；完整循环包含多个会话。可以在已安装的 `harness2-mode` 配置中修改 `timeout`、`k` 或 `outputRoot`。状态命令显示当前产物路径，旁边的日志文件记录进度。失败或取消的运行保留产物，并且不视为成功结果。

使用上述 Python 环境查看所有会话的状态。查看器默认选择最新的循环；如需查看其他循环，请传入 `/harness2 status` 显示的路径：

```sh
watch -n 2 harness2-dsh-status
watch -n 2 harness2-dsh-status --cycle /absolute/path/to/cycles/<cycle-id>
```

外层聊天中的 `Deep diving` 表示正在等待循环。查看器显示已记录的步骤、阶段、终止原因和事件时间间隔，不显示模型或工具载荷。停留在 `step_start` 可能是在等待回复或工具；事件时间间隔不代表模型处于空闲状态。`max-tokens` 表示模型输出预算已用尽，与会话时限不同。日志记录失败尝试、重试和最终循环结果。改进会话的记录保存在循环的 `audit/` 中；查看器也会找到日志中关联到 `/tmp` 的旧改进会话记录。

查看器也显示后端错误消息。失败的循环会在 `result.json` 中保留递归摘要和执行失败报告。失败卡片显示失败的最终执行及其后端原因，并提供进度日志路径，不附加已记录的心跳行。更新扩展不会重写历史失败卡片。

每次项目副本执行都通过原生 `harness2_finish` 工具结束，该工具终结当前轮次，无需模型再生成回复。先将完整交付物和验证报告保存在工作区文件中，再提交如实的 `summary` 和相对路径 `report_path`。`HARNESS2_DSH_HANDOFF_MAX_CHARS` 限制摘要长度（默认 2000 个 Unicode 字符）。报告必须是工作区内已存在且非空的普通文件；符号链接和工作区外路径会被拒绝。交接被接受后，后续工具调用会被阻止。基线、改进和自定义 harness 执行都必须具备已记录的成功交接、正常完成的持久化轮次和零进程退出码。普通最终文本和 `max-tokens` 仍视为失败。模型输出预算保持不变。

支持文本任务和项目文件。聊天附件请使用普通 dsh。Git 项目的快照选择已跟踪文件和未被忽略的未跟踪输入。Git 子模块和嵌套仓库会被排除，不遍历其内容，因此忽略的构建目录和本地参考仓库不会进入快照。普通文件夹使用运行目录和凭据过滤规则。内部符号链接会重新定位到各个副本中；指向项目外部或失效的链接会被拒绝。

默认限制仍为 100 MB 和 10,000 个条目。需要时可在已安装的插件配置中调整 `snapshotMaxBytes`、`snapshotMaxFiles` 和项目相对路径的 `snapshotExclude` 通配符。`snapshot.json` 记录字节数、文件数、最大的选中文件和排除原因（包括 Git 子模块）；规划失败时仍会保留此文件，并指出超过限制的指标与路径。

失败后，请重新发送原始任务以创建新的循环。旧失败卡片仍然记录原始尝试。移除集成：

```sh
python apps/cli/config/examples/harness2/install.py --profile web --uninstall
```

## 无需模型密钥的验证

profile 测试使用已安装的 dsh 连接 localhost 假模型，检查命令输出和持久化事件，并执行真正的 Python 循环。它不能证明生产推理服务的行为：

```sh
HARNESS2_TEST_DSH_COMMAND="$HARNESS2_DSH_COMMAND" \
  python -m unittest discover -s apps/cli/tests/profiles/harness2 -v
```
