class ParticleSystem {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
        this.symbols = ['+', '-', '*', '/', '<', '>', '=', '∞'];
        this.techSymbols = ['KIMI', 'AI', 'GPT', 'ML', 'CODE', 'DATA', 'TECH', '{ }', '</>', '⚡'];
        
        this.init();
        this.animate();
        window.addEventListener('resize', () => this.init());
    }

    init() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.particles = [];
        
        const particleCount = Math.floor((this.canvas.width * this.canvas.height) / 15000);
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push(this.createParticle());
        }
    }

    createParticle() {
        const types = ['number', 'symbol', 'trading', 'dot'];
        const type = types[Math.floor(Math.random() * types.length)];
        
        let content = '';
        if (type === 'number') {
            content = this.numbers[Math.floor(Math.random() * this.numbers.length)];
        } else if (type === 'symbol') {
            content = this.symbols[Math.floor(Math.random() * this.symbols.length)];
        } else if (type === 'trading') {
            content = this.techSymbols[Math.floor(Math.random() * this.techSymbols.length)];
        }
        
        return {
            x: Math.random() * this.canvas.width,
            y: Math.random() * this.canvas.height,
            size: Math.random() * (type === 'trading' ? 14 : 18) + (type === 'dot' ? 2 : 8),
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            opacity: Math.random() * 0.3 + 0.1,
            type: type,
            content: content,
            pulse: Math.random() * Math.PI * 2
        };
    }

    drawParticle(particle) {
        this.ctx.save();
        
        particle.pulse += 0.02;
        const pulseOpacity = particle.opacity * (0.8 + Math.sin(particle.pulse) * 0.2);
        
        if (particle.type === 'dot') {
            const gradient = this.ctx.createRadialGradient(
                particle.x, particle.y, 0,
                particle.x, particle.y, particle.size
            );
            gradient.addColorStop(0, `rgba(0, 255, 136, ${pulseOpacity})`);
            gradient.addColorStop(1, `rgba(0, 255, 136, 0)`);
            
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
        } else {
            this.ctx.fillStyle = `rgba(0, 255, 136, ${pulseOpacity})`;
            this.ctx.font = `${particle.size}px 'Inter', monospace`;
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            
            if (particle.type === 'trading') {
                this.ctx.font = `bold ${particle.size}px 'Inter', monospace`;
            }
            
            this.ctx.shadowBlur = 10;
            this.ctx.shadowColor = 'rgba(0, 255, 136, 0.5)';
            this.ctx.fillText(particle.content, particle.x, particle.y);
        }
        
        this.ctx.restore();
    }

    updateParticle(particle) {
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        
        if (particle.x < 0 || particle.x > this.canvas.width) {
            particle.speedX *= -1;
        }
        if (particle.y < 0 || particle.y > this.canvas.height) {
            particle.speedY *= -1;
        }
        
        particle.x = Math.max(0, Math.min(this.canvas.width, particle.x));
        particle.y = Math.max(0, Math.min(this.canvas.height, particle.y));
    }

    drawConnections() {
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    this.ctx.strokeStyle = `rgba(0, 255, 136, ${0.1 * (1 - distance / 150)})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.drawConnections();
        
        this.particles.forEach(particle => {
            this.updateParticle(particle);
            this.drawParticle(particle);
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ParticleSystem('particles-canvas');
});
