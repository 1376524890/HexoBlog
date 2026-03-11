#!/bin/bash

# WJX Automator 快速启动脚本
# 使用方法：./quickstart.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 打印彩色输出
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 Python3，请先安装 Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_info "Python 版本：$python_version"
}

# 安装依赖
install_deps() {
    print_info "检查 Python 依赖..."
    
    if [ ! -d "venv" ]; then
        print_info "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    print_info "安装依赖包..."
    pip install -r requirements.txt --quiet
    
    print_success "依赖安装完成！"
}

# 检查 Chrome 浏览器
check_chrome() {
    print_info "检查 Chrome 浏览器..."
    
    if command -v google-chrome &> /dev/null; then
        chrome_version=$(google-chrome --version)
        print_success "Chrome 版本：$chrome_version"
    elif command -v chromium-browser &> /dev/null; then
        chrome_version=$(chromium-browser --version)
        print_success "Chromium 版本：$chrome_version"
    elif command -v chromium &> /dev/null; then
        chrome_version=$(chromium --version)
        print_success "Chromium 版本：$chrome_version"
    else
        print_warning "未找到 Chrome 或 Chromium 浏览器"
        print_info "请访问 https://www.google.com/chrome/ 下载并安装"
    fi
}

# 运行测试
run_test() {
    print_info "运行干燥测试模式..."
    python3 main.py --dry-run --verbose
}

# 实际运行
run_actual() {
    print_info "开始填写问卷..."
    python3 main.py "$@"
}

# 显示使用帮助
show_help() {
    cat << EOF
WJX Automator - 问卷星自动填写系统

用法：$0 [命令] [选项]

命令:
    setup         安装依赖和配置环境
    test          运行干燥测试（仅生成答案示例）
    run           实际填写问卷
    help          显示此帮助信息

选项:
    --workers N   设置并发线程数 (默认：5)
    --data FILE   指定数据文件路径
    --config FILE 指定配置文件路径
    --verbose     详细日志模式
    --dry-run     干燥测试模式

示例:
    # 安装环境
    $0 setup
    
    # 运行测试
    $0 test
    
    # 实际填写（5 线程并发）
    $0 run --workers 5
    
    # 详细日志模式
    $0 run --verbose --workers 10

更多信息请查看 README.md
EOF
}

# 主程序
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        setup)
            print_info "开始初始化环境..."
            check_python
            install_deps
            check_chrome
            print_success "环境初始化完成！"
            ;;
        test)
            check_python
            run_test
            ;;
        run)
            check_python
            run_actual "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令：$command"
            show_help
            exit 1
            ;;
    esac
}

# 执行
main "$@"
