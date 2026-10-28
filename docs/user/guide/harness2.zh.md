# 在聊天中运行 Harness²

[English](harness2.md) | 中文

此可选集成向 dsh 聊天添加 `/harness2 on|off|status`。启用后，每个新的文本任务先在项目副本中执行完整的 Harness² 适配循环，然后 dsh 接收选定的回复、修改和 harness。新聊天默认关闭此模式。

## 安装

使用此 fork 的 `feat/harness2-integration` 分支、Node 24、Python 3.12 或 3.13，以及已经配置模型的 dsh 0.2.0-rc.2。此示例尚未验证其他 dsh 版本。在本仓库中运行：

```sh
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install 'harness2 @ git+https://github.com/LuciyVI/harness2.git@dsh-integration-v2'
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
