# api_techlog/management/commands/import_blogmark.py
#
# 使い方:
#   python manage.py import_blogmark blogmark_export.json --user=your@email.com
#   python manage.py import_blogmark blogmark_export.json --user=your@email.com --dry-run
#   python manage.py import_blogmark blogmark_export.json --user=your@email.com --published-only

import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    help = 'blogmark_export.json を api_techlog にインポートする'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            help='エクスポートされたJSONファイルのパス（例: blogmark_export.json）'
        )
        parser.add_argument(
            '--user', required=True,
            help='投稿者のメールアドレス'
        )
        parser.add_argument(
            '--published-only', action='store_true',
            help='公開済み（status=2）の記事のみインポート'
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='DBに保存せずに確認するテスト実行'
        )

    def handle(self, *args, **options):
        from api_techlog.models import Post as NewPost, Category as NewCategory

        User = get_user_model()
        dry_run = options['dry_run']

        # ── JSONファイル読み込み ──────────────────────────────────
        json_path = Path(options['json_file'])
        if not json_path.exists():
            raise CommandError(f'ファイルが見つかりません: {json_path}')

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        categories = data.get('categories', [])
        posts      = data.get('posts', [])

        self.stdout.write(f'JSONファイル: {json_path}')
        self.stdout.write(f'  カテゴリ数: {len(categories)}')
        self.stdout.write(f'  記事数:     {len(posts)}')

        # ── 投稿者確認 ───────────────────────────────────────────
        try:
            author = User.objects.get(email=options['user'])
        except User.DoesNotExist:
            raise CommandError(f"ユーザーが見つかりません: {options['user']}")

        self.stdout.write(f'投稿者: {author.email}')
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN】DBには保存されません\n'))

        # ── カテゴリのマッピング作成 ─────────────────────────────
        self.stdout.write('--- カテゴリ ---')
        cat_map = {}  # { old_id: NewCategory instance }

        for cat in categories:
            old_id = cat['id']
            name   = cat['name']
            if not dry_run:
                new_cat, created = NewCategory.objects.get_or_create(name=name)
            else:
                try:
                    new_cat = NewCategory.objects.get(name=name)
                    created = False
                except NewCategory.DoesNotExist:
                    new_cat = type('Cat', (), {'pk': None, 'name': name})()
                    created = True

            cat_map[old_id] = new_cat
            mark = self.style.SUCCESS('[新規]') if created else '[既存]'
            self.stdout.write(f'  {mark} {name}')

        self.stdout.write(f'  → 合計 {len(cat_map)} カテゴリ\n')

        # ── 記事インポート ───────────────────────────────────────
        self.stdout.write('--- 記事インポート ---')

        if options['published_only']:
            posts = [p for p in posts if p.get('status') == 2]
            self.stdout.write('  （公開済みのみ対象）')

        self.stdout.write(f'  対象記事数: {len(posts)} 件\n')

        ok = skip_no_content = skip_no_cat = 0

        with transaction.atomic():
            for i, post in enumerate(posts, 1):

                # 本文の組み立て
                content = (post.get('content') or '').strip()
                if not content:
                    content = (post.get('text') or '').strip()

                codememo = (post.get('codememo') or '').strip()
                if codememo:
                    content += (
                        '\n\n## サンプルコード\n\n'
                        f'```\n{codememo}\n```'
                    )

                if not content:
                    self.stdout.write(
                        self.style.WARNING(f'  SKIP [本文なし]: {post["title"]}')
                    )
                    skip_no_content += 1
                    continue

                new_cat = cat_map.get(post.get('category_id'))
                if not new_cat or (not dry_run and not new_cat.pk):
                    self.stdout.write(
                        self.style.WARNING(f'  SKIP [カテゴリなし]: {post["title"]}')
                    )
                    skip_no_cat += 1
                    continue

                status     = 'published' if post.get('status') == 2 else 'draft'
                created_at = parse_datetime(post.get('created_at', '')) or None

                if not dry_run:
                    NewPost.objects.create(
                        title=post['title'],
                        content=content,
                        category=new_cat,
                        author=author,
                        status=status,
                        views=post.get('views', 0),
                        created_at=created_at,
                    )

                ok += 1
                if ok % 50 == 0:
                    self.stdout.write(f'  ... {ok}/{len(posts)} 件処理中')

            if dry_run:
                transaction.set_rollback(True)

        # ── サマリー ─────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ 完了'))
        self.stdout.write(f'  インポート成功:    {ok} 件')
        self.stdout.write(f'  スキップ(本文なし): {skip_no_content} 件')
        self.stdout.write(f'  スキップ(カテゴリ): {skip_no_cat} 件')
        if dry_run:
            self.stdout.write(self.style.WARNING('\n  ※ DRY RUN のため実際には保存されていません'))
