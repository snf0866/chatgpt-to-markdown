#!/usr/bin/env python3
"""
ChatGPT to Markdown with configuration support
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import sync_playwright


@dataclass
class Config:
    """Configuration container"""
    output_dir: str = "."
    format: str = "standard"
    obsidian_vault: Optional[str] = None
    obsidian_slipbox: str = "000_Slipbox/chatgpt_dialogues"
    obsidian_blog: str = "100_blog_drafts"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.2
    browser_headless: bool = True
    browser_timeout: int = 30000
    insights_language: str = "auto"
    
    @classmethod
    def from_file(cls, config_path: str) -> Config:
        """Load configuration from YAML file"""
        config = cls()
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                if data and 'output' in data:
                    config.output_dir = data['output'].get('directory', config.output_dir)
                    config.format = data['output'].get('format', config.format)
                    
                    if 'obsidian' in data['output']:
                        obs = data['output']['obsidian']
                        config.obsidian_vault = obs.get('vault_path')
                        if config.obsidian_vault:
                            config.obsidian_vault = os.path.expanduser(config.obsidian_vault)
                        config.obsidian_slipbox = obs.get('slipbox_path', config.obsidian_slipbox)
                        config.obsidian_blog = obs.get('blog_path', config.obsidian_blog)
                
                if data and 'openai' in data:
                    config.openai_api_key = data['openai'].get('api_key')
                    config.openai_model = data['openai'].get('model', config.openai_model)
                    config.openai_temperature = data['openai'].get('temperature', config.openai_temperature)
                
                if data and 'browser' in data:
                    config.browser_headless = data['browser'].get('headless', config.browser_headless)
                    config.browser_timeout = data['browser'].get('timeout', config.browser_timeout)
                
                if data and 'language' in data:
                    config.insights_language = data['language'].get('insights_language', config.insights_language)
        
        # Override with environment variables
        config.openai_api_key = config.openai_api_key or os.environ.get("OPENAI_API_KEY")
        
        return config


@dataclass
class Message:
    speaker: str  # "User" | "ChatGPT"
    content: str


def extract_messages_with_playwright(url: str, config: Config) -> List[Message]:
    """Extract messages from ChatGPT share URL using Playwright"""
    
    messages = []
    
    with sync_playwright() as p:
        print("🌐 Launching browser...")
        browser = p.chromium.launch(headless=config.browser_headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        try:
            print(f"📍 Accessing URL: {url}")
            page.goto(url, wait_until="networkidle", timeout=config.browser_timeout)
            
            print("⏳ Waiting for page to load...")
            page.wait_for_timeout(3000)
            
            print("🔍 Extracting conversation data...")
            js_script = """
            () => {
                // Method 1: Extract from React Fiber
                const root = document.querySelector('#__next');
                if (root && root._reactRootContainer) {
                    const fiber = root._reactRootContainer._internalRoot.current;
                    
                    function findData(node, depth = 0) {
                        if (depth > 50) return null;
                        
                        if (node && node.memoizedProps) {
                            if (node.memoizedProps.sharedConversation) {
                                return node.memoizedProps.sharedConversation;
                            }
                            if (node.memoizedProps.conversation) {
                                return node.memoizedProps.conversation;
                            }
                            if (node.memoizedProps.messages) {
                                return node.memoizedProps.messages;
                            }
                        }
                        
                        if (node && node.child) {
                            const result = findData(node.child, depth + 1);
                            if (result) return result;
                        }
                        
                        if (node && node.sibling) {
                            const result = findData(node.sibling, depth + 1);
                            if (result) return result;
                        }
                        
                        return null;
                    }
                    
                    const data = findData(fiber);
                    if (data) return data;
                }
                
                // Method 2: Extract from __NEXT_DATA__
                const nextDataScript = document.getElementById('__NEXT_DATA__');
                if (nextDataScript) {
                    const data = JSON.parse(nextDataScript.textContent);
                    const props = data?.props?.pageProps;
                    if (props?.sharedConversation) {
                        return props.sharedConversation;
                    }
                }
                
                // Method 3: Extract from window.__remixContext
                if (window.__remixContext) {
                    const loaderData = window.__remixContext?.state?.loaderData;
                    for (const key in loaderData) {
                        if (loaderData[key]?.sharedConversation) {
                            return loaderData[key].sharedConversation;
                        }
                    }
                }
                
                // Method 4: Extract from DOM elements
                const elements = [];
                
                const selectors = [
                    '[data-message-author-role]',
                    '[data-testid*="conversation-turn"]',
                    '.text-message',
                    '.markdown',
                    'article'
                ];
                
                for (const selector of selectors) {
                    const found = document.querySelectorAll(selector);
                    if (found.length > 0) {
                        found.forEach(el => {
                            const text = el.innerText || el.textContent;
                            const role = el.getAttribute('data-message-author-role') || 
                                        (el.className.includes('user') ? 'user' : 'assistant');
                            if (text && text.trim()) {
                                elements.push({role, text: text.trim()});
                            }
                        });
                        if (elements.length > 0) break;
                    }
                }
                
                if (elements.length > 0) {
                    return {dom_elements: elements};
                }
                
                return null;
            }
            """
            
            result = page.evaluate(js_script)
            
            if result:
                print(f"✅ Data extracted successfully")
                
                # Process DOM elements
                if isinstance(result, dict) and 'dom_elements' in result:
                    for elem in result['dom_elements']:
                        text = elem['text']
                        role = elem.get('role', 'assistant')
                        
                        if not is_ui_text(text):
                            speaker = "User" if role == "user" else "ChatGPT"
                            messages.append(Message(speaker, text))
                
                # Process mapping data
                elif isinstance(result, dict) and 'mapping' in result:
                    mapping = result['mapping']
                    nodes = []
                    
                    for node_id, node in mapping.items():
                        if 'message' in node and node['message']:
                            msg = node['message']
                            role = msg.get('author', {}).get('role', 'assistant')
                            parts = msg.get('content', {}).get('parts', [])
                            create_time = msg.get('create_time', 0)
                            
                            content = '\n'.join([str(p) for p in parts if p])
                            speaker = "User" if role == "user" else "ChatGPT"
                            
                            if content and not is_ui_text(content):
                                nodes.append((create_time, Message(speaker, content)))
                    
                    nodes.sort(key=lambda x: x[0])
                    messages = [msg for _, msg in nodes]
                
                # Process linear conversation data
                elif isinstance(result, dict) and 'linear_conversation' in result:
                    for item in result['linear_conversation']:
                        if 'message' in item:
                            msg = item['message']
                            role = msg.get('author', {}).get('role', 'assistant')
                            content = msg.get('content', {}).get('parts', [''])[0]
                            speaker = "User" if role == "user" else "ChatGPT"
                            if content and not is_ui_text(content):
                                messages.append(Message(speaker, content))
            
            print(f"📊 Extracted {len(messages)} messages")
            
        finally:
            browser.close()
            print("🔒 Browser closed")
    
    return messages


def is_ui_text(text: str) -> bool:
    """Check if text is UI element text"""
    ui_patterns = [
        "Login", "Sign up", "Terms of Use", "Privacy Policy",
        "Continue with", "Email address", "Welcome back",
        "Create your account", "Remember me", "Don't have an account"
    ]
    return any(pattern in text for pattern in ui_patterns)


def generate_insights_and_tags(messages: List[Message], config: Config) -> Tuple[List[str], List[str]]:
    """Generate insights and tags using OpenAI API"""
    if not config.openai_api_key:
        return [], []
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=config.openai_api_key)
        
        combined = []
        total_chars = 0
        for m in messages:
            chunk = f"{m.speaker}: {m.content}\n\n"
            combined.append(chunk)
            total_chars += len(chunk)
            if total_chars > 12000:
                break
        convo = "".join(combined)
        
        if len(convo) < 50:
            return [], []
        
        # Determine language for insights
        lang_instruction = ""
        if config.insights_language == "ja":
            lang_instruction = "Return insights and tags in Japanese."
        elif config.insights_language == "en":
            lang_instruction = "Return insights and tags in English."
        else:
            lang_instruction = "Return insights and tags in the same language as the conversation."
        
        prompt = (
            f"Extract key insights and tags from this ChatGPT conversation.\n"
            f"{lang_instruction}\n"
            "Return JSON only:\n"
            '{"insights": ["insight1", "insight2", ...], "tags": ["#tag1", "#tag2", ...]}'
        )
        
        response = client.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts insights from conversations."},
                {"role": "user", "content": prompt + "\n\n" + convo},
            ],
            temperature=config.openai_temperature,
            response_format={"type": "json_object"},
        )
        
        text = response.choices[0].message.content or "{}"
        data = json.loads(text)
        insights = data.get("insights", [])
        tags = data.get("tags", [])
        
        return insights[:5], tags[:7]
        
    except Exception as e:
        print(f"⚠️ API error: {e}")
        return [], []


def create_markdown(messages: List[Message], insights: List[str] = None, tags: List[str] = None, format_type: str = "standard") -> str:
    """Create markdown content from messages"""
    
    # Extract title from first user message
    title = "ChatGPT Conversation"
    for m in messages:
        if m.speaker == "User":
            title = m.content[:100].replace("\n", " ")
            break
    
    # Build markdown
    lines = []
    
    if format_type == "obsidian":
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        if tags:
            lines.append(f"Tags: {' '.join(tags)}")
        lines.append("")
    else:
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("")
    
    if insights:
        lines.append("## Key Insights")
        lines.append("")
        for insight in insights:
            lines.append(f"- {insight}")
        lines.append("")
    
    lines.append("## Conversation")
    lines.append("")
    
    for i, message in enumerate(messages, 1):
        emoji = "👤" if message.speaker == "User" else "🤖"
        lines.append(f"### {emoji} {message.speaker}")
        lines.append("")
        lines.append(message.content)
        lines.append("")
    
    if format_type == "blog":
        lines.append("---")
        lines.append("")
        lines.append("*This conversation was exported from ChatGPT.*")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Export ChatGPT conversations as beautiful markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://chatgpt.com/share/...
  %(prog)s https://chatgpt.com/share/... --format obsidian
  %(prog)s https://chatgpt.com/share/... --output ./conversations
  %(prog)s https://chatgpt.com/share/... --config config.yaml
  %(prog)s https://chatgpt.com/share/... --no-insights --show-browser
        """
    )
    
    parser.add_argument("url", help="ChatGPT share URL")
    parser.add_argument("--config", type=str, default="config.yaml",
                        help="Configuration file path (default: config.yaml)")
    parser.add_argument("--format", choices=["standard", "obsidian", "blog"],
                        help="Output format (overrides config)")
    parser.add_argument("--output", type=str,
                        help="Output directory (overrides config)")
    parser.add_argument("--no-insights", action="store_true",
                        help="Skip AI insights generation")
    parser.add_argument("--show-browser", action="store_true",
                        help="Show browser window (for debugging)")
    parser.add_argument("--timeout", type=int,
                        help="Timeout in milliseconds (overrides config)")
    parser.add_argument("--obsidian-vault", type=str,
                        help="Obsidian vault path (overrides config)")
    parser.add_argument("--is-blog", action="store_true",
                        help="Save as blog draft in Obsidian vault")
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.from_file(args.config)
    
    # Override config with command line arguments
    if args.format:
        config.format = args.format
    if args.output:
        config.output_dir = args.output
    if args.show_browser:
        config.browser_headless = False
    if args.timeout:
        config.browser_timeout = args.timeout
    if args.obsidian_vault:
        config.obsidian_vault = os.path.expanduser(args.obsidian_vault)
    
    print(f"\n🚀 ChatGPT to Markdown Exporter")
    print(f"📍 URL: {args.url}")
    
    # Extract messages
    messages = extract_messages_with_playwright(args.url, config)
    
    if not messages:
        print("\n❌ Failed to extract messages")
        print("💡 Tips:")
        print("  1. Ensure the URL is a valid share link")
        print("  2. Try using --show-browser to debug")
        print("  3. Increase timeout with --timeout 60000")
        return 1
    
    # Generate insights and tags
    insights = []
    tags = []
    if not args.no_insights:
        print("\n💭 Generating insights and tags...")
        insights, tags = generate_insights_and_tags(messages, config)
        if insights:
            print(f"✅ Generated {len(insights)} insights")
        if tags:
            print(f"✅ Generated {len(tags)} tags")
    
    # Create markdown
    markdown = create_markdown(messages, insights, tags, config.format)
    
    # Generate filename
    title_seed = ""
    for m in messages:
        if m.speaker == "User":
            title_seed = re.sub(r"[^\w\s\-]", "", m.content[:50])
            break
    
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-chatgpt-{title_seed or 'conversation'}.md"
    
    # Determine output path
    if config.obsidian_vault and config.format == "obsidian":
        # Use Obsidian vault structure
        vault_path = Path(config.obsidian_vault)
        if args.is_blog:
            output_dir = vault_path / config.obsidian_blog
        else:
            output_dir = vault_path / config.obsidian_slipbox
    else:
        # Use regular output directory
        output_dir = Path(config.output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    
    # Save file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"\n✅ Exported to: {filepath}")
    print(f"📝 Messages: {len(messages)}")
    
    if insights:
        print(f"💡 Insights: {len(insights)}")
    if tags:
        print(f"🏷️  Tags: {', '.join(tags)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())