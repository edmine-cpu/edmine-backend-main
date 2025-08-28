"""
Антифрод система для защиты платформы
"""
import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import json
from collections import defaultdict


class AntifraudSystem:
    def __init__(self):
        # Хранилище активности пользователей
        self.user_activity: Dict[int, List[Dict]] = defaultdict(list)
        self.ip_activity: Dict[str, List[Dict]] = defaultdict(list)
        self.suspicious_patterns: Dict[str, int] = defaultdict(int)
        
        # Настройки лимитов
        self.LIMITS = {
            'max_requests_per_minute': 60,
            'max_requests_per_hour': 300,
            'max_login_attempts': 5,
            'max_bids_per_hour': 10,
            'max_messages_per_minute': 20,
            'suspicious_score_threshold': 100
        }
    
    def _get_time_window(self, minutes: int) -> datetime:
        """Получить время окна для проверки"""
        return datetime.now() - timedelta(minutes=minutes)
    
    def _clean_old_records(self, user_id: Optional[int] = None, ip: Optional[str] = None):
        """Очистить старые записи активности"""
        cutoff_time = self._get_time_window(60)  # Храним данные час
        
        if user_id and user_id in self.user_activity:
            self.user_activity[user_id] = [
                record for record in self.user_activity[user_id]
                if datetime.fromisoformat(record['timestamp']) > cutoff_time
            ]
        
        if ip and ip in self.ip_activity:
            self.ip_activity[ip] = [
                record for record in self.ip_activity[ip]
                if datetime.fromisoformat(record['timestamp']) > cutoff_time
            ]
    
    async def log_activity(self, user_id: Optional[int], ip: str, action: str, details: Dict = None):
        """Логировать активность пользователя"""
        timestamp = datetime.now().isoformat()
        activity_record = {
            'timestamp': timestamp,
            'action': action,
            'details': details or {},
            'ip': ip
        }
        
        if user_id:
            self.user_activity[user_id].append(activity_record)
            self._clean_old_records(user_id=user_id)
        
        self.ip_activity[ip].append(activity_record)
        self._clean_old_records(ip=ip)
    
    async def check_rate_limits(self, user_id: Optional[int], ip: str, action: str) -> Dict:
        """Проверить лимиты скорости запросов"""
        result = {
            'allowed': True,
            'reason': '',
            'retry_after': 0,
            'risk_score': 0
        }
        
        now = datetime.now()
        minute_ago = self._get_time_window(1)
        hour_ago = self._get_time_window(60)
        
        # Проверка по IP
        ip_records = [
            r for r in self.ip_activity.get(ip, [])
            if datetime.fromisoformat(r['timestamp']) > minute_ago
        ]
        
        if len(ip_records) > self.LIMITS['max_requests_per_minute']:
            result['allowed'] = False
            result['reason'] = 'Too many requests per minute from this IP'
            result['retry_after'] = 60
            result['risk_score'] += 50
            return result
        
        # Проверка по пользователю (если авторизован)
        if user_id:
            user_records = [
                r for r in self.user_activity.get(user_id, [])
                if datetime.fromisoformat(r['timestamp']) > hour_ago
            ]
            
            if len(user_records) > self.LIMITS['max_requests_per_hour']:
                result['allowed'] = False
                result['reason'] = 'Too many requests per hour for this user'
                result['retry_after'] = 3600
                result['risk_score'] += 30
                return result
            
            # Специфические проверки по действиям
            action_specific_checks = await self._check_action_specific_limits(
                user_id, action, user_records, minute_ago, hour_ago
            )
            
            if not action_specific_checks['allowed']:
                return action_specific_checks
        
        return result
    
    async def _check_action_specific_limits(self, user_id: int, action: str, 
                                          user_records: List, minute_ago: datetime, 
                                          hour_ago: datetime) -> Dict:
        """Проверка специфических лимитов по действиям"""
        result = {'allowed': True, 'reason': '', 'retry_after': 0, 'risk_score': 0}
        
        if action == 'login':
            login_attempts = [
                r for r in user_records
                if r['action'] == 'login' and datetime.fromisoformat(r['timestamp']) > minute_ago
            ]
            if len(login_attempts) > self.LIMITS['max_login_attempts']:
                result['allowed'] = False
                result['reason'] = 'Too many login attempts'
                result['retry_after'] = 300  # 5 минут
                result['risk_score'] += 70
        
        elif action == 'create_bid':
            bid_creations = [
                r for r in user_records
                if r['action'] == 'create_bid' and datetime.fromisoformat(r['timestamp']) > hour_ago
            ]
            if len(bid_creations) > self.LIMITS['max_bids_per_hour']:
                result['allowed'] = False
                result['reason'] = 'Too many bids created per hour'
                result['retry_after'] = 3600
                result['risk_score'] += 40
        
        elif action == 'send_message':
            messages = [
                r for r in user_records
                if r['action'] == 'send_message' and datetime.fromisoformat(r['timestamp']) > minute_ago
            ]
            if len(messages) > self.LIMITS['max_messages_per_minute']:
                result['allowed'] = False
                result['reason'] = 'Too many messages per minute'
                result['retry_after'] = 60
                result['risk_score'] += 60
        
        return result
    
    async def detect_suspicious_patterns(self, user_id: Optional[int], ip: str, 
                                       request_data: Dict) -> Dict:
        """Обнаружение подозрительных паттернов"""
        risk_score = 0
        patterns = []
        
        # Проверка на ботов (очень быстрые запросы)
        if user_id:
            recent_activities = [
                r for r in self.user_activity.get(user_id, [])
                if datetime.fromisoformat(r['timestamp']) > self._get_time_window(1)
            ]
            
            if len(recent_activities) > 10:  # Более 10 запросов в минуту
                risk_score += 30
                patterns.append('rapid_requests')
        
        # Проверка повторяющихся данных
        if 'email' in request_data:
            email_hash = hashlib.md5(request_data['email'].encode()).hexdigest()
            recent_email_usage = self.suspicious_patterns.get(f'email_{email_hash}', 0)
            if recent_email_usage > 3:
                risk_score += 50
                patterns.append('email_reuse')
            self.suspicious_patterns[f'email_{email_hash}'] += 1
        
        # Проверка User-Agent (если есть)
        if 'user_agent' in request_data:
            ua = request_data['user_agent']
            if 'bot' in ua.lower() or 'crawler' in ua.lower():
                risk_score += 80
                patterns.append('bot_user_agent')
        
        # Проверка на множественные аккаунты с одного IP
        unique_users_from_ip = len(set(
            r.get('details', {}).get('user_id') for r in self.ip_activity.get(ip, [])
            if r.get('details', {}).get('user_id')
        ))
        
        if unique_users_from_ip > 10:
            risk_score += 40
            patterns.append('multiple_accounts_same_ip')
        
        return {
            'risk_score': risk_score,
            'patterns': patterns,
            'is_suspicious': risk_score >= self.LIMITS['suspicious_score_threshold']
        }
    
    async def should_require_captcha(self, user_id: Optional[int], ip: str) -> bool:
        """Определить, нужна ли капча"""
        if user_id:
            user_records = self.user_activity.get(user_id, [])
            recent_fails = [
                r for r in user_records
                if (r['action'] in ['login_failed', 'registration_failed'] and 
                    datetime.fromisoformat(r['timestamp']) > self._get_time_window(10))
            ]
            if len(recent_fails) >= 3:
                return True
        
        # Проверка по IP
        ip_records = self.ip_activity.get(ip, [])
        recent_ip_fails = [
            r for r in ip_records
            if (r['action'] in ['login_failed', 'registration_failed'] and 
                datetime.fromisoformat(r['timestamp']) > self._get_time_window(10))
        ]
        
        return len(recent_ip_fails) >= 5
    
    async def should_block_user(self, user_id: int) -> Dict:
        """Определить, нужно ли заблокировать пользователя"""
        user_records = self.user_activity.get(user_id, [])
        
        # Проверка на массовый спам
        recent_violations = [
            r for r in user_records
            if (r['action'] in ['spam_detected', 'policy_violation'] and 
                datetime.fromisoformat(r['timestamp']) > self._get_time_window(60))
        ]
        
        if len(recent_violations) >= 5:
            return {
                'should_block': True,
                'reason': 'Multiple policy violations',
                'duration': 86400  # 24 часа
            }
        
        # Проверка на фрод
        fraud_indicators = [
            r for r in user_records
            if (r['action'] in ['payment_fraud', 'fake_reviews'] and 
                datetime.fromisoformat(r['timestamp']) > self._get_time_window(1440))  # 24 часа
        ]
        
        if len(fraud_indicators) >= 1:
            return {
                'should_block': True,
                'reason': 'Fraud detected',
                'duration': 604800  # 7 дней
            }
        
        return {'should_block': False}
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Получить статистику пользователя"""
        records = self.user_activity.get(user_id, [])
        
        return {
            'total_activities': len(records),
            'recent_activities_1h': len([
                r for r in records
                if datetime.fromisoformat(r['timestamp']) > self._get_time_window(60)
            ]),
            'risk_indicators': len([
                r for r in records
                if r['action'] in ['login_failed', 'spam_detected', 'policy_violation']
            ])
        }


# Глобальный экземпляр антифрод системы
antifraud = AntifraudSystem()
