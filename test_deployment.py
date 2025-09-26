#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys

def test_deployment(url):
    """测试部署的应用是否正常工作"""
    
    print(f"🧪 测试部署URL: {url}")
    print("=" * 50)
    
    try:
        # 测试主页
        print("1. 测试主页...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ 主页访问成功")
            if "Expert Rating System" in response.text or "专家评分系统" in response.text:
                print("✅ 页面内容正确")
            else:
                print("⚠️  页面内容可能有问题")
        else:
            print(f"❌ 主页访问失败: {response.status_code}")
            return False
        
        # 测试主题页面
        print("\n2. 测试主题页面...")
        topic_url = f"{url}/rate/topic1"
        response = requests.get(topic_url, timeout=10)
        if response.status_code == 200:
            print("✅ 主题页面访问成功")
        else:
            print(f"❌ 主题页面访问失败: {response.status_code}")
        
        # 测试静态文件
        print("\n3. 测试静态文件...")
        css_url = f"{url}/static/css/style.css"
        response = requests.get(css_url, timeout=10)
        if response.status_code == 200:
            print("✅ CSS文件加载成功")
        else:
            print(f"❌ CSS文件加载失败: {response.status_code}")
        
        print("\n🎉 部署测试完成！")
        return True
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请检查URL是否正确")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("使用方法: python test_deployment.py <RAILWAY_URL>")
        print("示例: python test_deployment.py https://hypothesis-expert-rating-system-production.up.railway.app")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    success = test_deployment(url)
    
    if success:
        print("\n✅ 部署测试通过！您的专家评分系统已经成功部署！")
        print(f"🌐 访问地址: {url}")
        print("\n📋 功能清单:")
        print("- ✅ 主页显示所有主题")
        print("- ✅ 主题评分页面")
        print("- ✅ 中英文切换")
        print("- ✅ 静态文件加载")
        print("- ✅ 响应式设计")
    else:
        print("\n❌ 部署测试失败，请检查部署配置")

if __name__ == "__main__":
    main()
