"""
Psychologist Model
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, or_
from sqlalchemy.orm import relationship, Session, joinedload
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session
from app.models.tabelas_associacao import psychologist_specialties, psychologist_approaches

class Psychologist(Base):
    __tablename__ = "psychologists"
    
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), unique=True, nullable=False)
    crp = Column(String, unique=True, nullable=False)  # Conselho Regional de Psicologia
    biografia = Column("bio", Text)
    anos_experiencia = Column("experience_years", Integer, default=0)
    preco_consulta = Column("consultation_price", Float)
    consulta_online = Column("online_consultation", Boolean, default=True)
    consulta_presencial = Column("in_person_consultation", Boolean, default=False)
    endereco = Column("address", String)
    cidade = Column("city", String)
    estado = Column("state", String)
    cep = Column("zip_code", String)
    foto_perfil = Column("profile_picture", String)
    avaliacao = Column("rating", Float, default=0.0)
    total_avaliacoes = Column("total_reviews", Integer, default=0)
    esta_verificado = Column("is_verified", Boolean, default=False)
    rejeitado = Column("rejected", Boolean, default=False)  # Indica se foi rejeitado pelo admin
    saldo = Column("balance", Float, default=0.0)  # Saldo disponível para saque
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="psychologist_profile")
    specialties = relationship("Specialty", secondary=psychologist_specialties, back_populates="psychologists")
    approaches = relationship("Approach", secondary=psychologist_approaches, back_populates="psychologists")
    reviews = relationship("Review", back_populates="psychologist")
    appointments = relationship("Appointment", back_populates="psychologist", overlaps="appointments")
    availability = relationship("PsychologistAvailability", back_populates="psychologist", overlaps="availability")
    withdrawals = relationship("Withdrawal", back_populates="psychologist", overlaps="withdrawals")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_psicologo: int, carregar_relacionamentos: bool = False) -> Optional["Psychologist"]:
        """Obter psicólogo por ID"""
        db = get_db_session()
        try:
            query = db.query(cls)
            if carregar_relacionamentos:
                query = query.options(
                    joinedload(cls.user),
                    joinedload(cls.specialties),
                    joinedload(cls.approaches)
                )
            return query.filter(cls.id == id_psicologo).first()
        finally:
            db.close()
    
    @classmethod
    def obter_por_user_id(cls, id_usuario: int) -> Optional["Psychologist"]:
        """Obter psicólogo por id_usuario"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id_usuario == id_usuario).first()
        finally:
            db.close()
    
    @classmethod
    def obter_por_crp(cls, crp: str) -> Optional["Psychologist"]:
        """Obter psicólogo por CRP"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.crp == crp).first()
        finally:
            db.close()
    
    @classmethod
    def listar_verificados(cls, pular: int = 0, limite: int = 20) -> List["Psychologist"]:
        """Listar psicólogos verificados"""
        db = get_db_session()
        try:
            return db.query(cls).options(
                joinedload(cls.user),
                joinedload(cls.specialties),
                joinedload(cls.approaches)
            ).filter(cls.esta_verificado == True).offset(pular).limit(limite).all()
        finally:
            db.close()
    
    @classmethod
    def listar_pendentes(cls) -> List["Psychologist"]:
        """Listar psicólogos pendentes de verificação (não rejeitados)"""
        db = get_db_session()
        try:
            query = db.query(cls).options(
                joinedload(cls.user),
                joinedload(cls.specialties),
                joinedload(cls.approaches)
            ).filter(cls.esta_verificado == False)
            
            # Filtrar rejeitados se o campo existir
            try:
                query = query.filter(cls.rejeitado == False)
            except Exception:
                # Se o campo não existir ainda, ignorar o filtro
                pass
            
            return query.all()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "Psychologist":
        """Criar novo psicólogo"""
        db = get_db_session()
        try:
            psicologo = cls(**kwargs)
            db.add(psicologo)
            db.commit()
            db.refresh(psicologo)
            return psicologo
        finally:
            db.close()
    
    @classmethod
    def criar_com_relacionamentos(
        cls,
        specialty_ids: Optional[List[int]] = None,
        approach_ids: Optional[List[int]] = None,
        **kwargs
    ) -> "Psychologist":
        """Criar psicólogo com especialidades e abordagens"""
        from app.models.especialidade import Specialty
        from app.models.tratamento import Approach
        
        db = get_db_session()
        try:
            psicologo = cls(**kwargs)
            db.add(psicologo)
            db.flush()  # Para obter o ID
            
            # Adicionar especialidades
            if specialty_ids and len(specialty_ids) > 0:
                especialidades = Specialty.obter_por_ids(specialty_ids)
                psicologo.specialties = especialidades
            else:
                psicologo.specialties = []
            
            # Adicionar abordagens
            if approach_ids and len(approach_ids) > 0:
                abordagens = Approach.obter_por_ids(approach_ids)
                psicologo.approaches = abordagens
            else:
                psicologo.approaches = []
            
            db.commit()
            db.refresh(psicologo)
            return psicologo
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "Psychologist":
        """Atualizar psicólogo"""
        db = get_db_session()
        try:
            psicologo = db.query(Psychologist).filter(Psychologist.id == self.id).first()
            if not psicologo:
                raise ValueError("Psicólogo não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(psicologo, key):
                    setattr(psicologo, key, value)
            db.commit()
            db.refresh(psicologo)
            return psicologo
        finally:
            db.close()
    
    def atualizar_com_relacionamentos(
        self,
        specialty_ids: Optional[List[int]] = None,
        approach_ids: Optional[List[int]] = None,
        **kwargs
    ) -> "Psychologist":
        """Atualizar psicólogo com especialidades e abordagens"""
        from app.models.especialidade import Specialty
        from app.models.tratamento import Approach
        
        db = get_db_session()
        try:
            psicologo = db.query(Psychologist).filter(Psychologist.id == self.id).first()
            if not psicologo:
                raise ValueError("Psicólogo não encontrado")
            
            # Atualizar campos simples
            for key, value in kwargs.items():
                if hasattr(psicologo, key):
                    setattr(psicologo, key, value)
            
            # Atualizar especialidades
            if specialty_ids is not None:
                if len(specialty_ids) > 0:
                    especialidades = Specialty.obter_por_ids(specialty_ids)
                    psicologo.specialties = especialidades
                else:
                    psicologo.specialties = []
            
            # Atualizar abordagens
            if approach_ids is not None:
                if len(approach_ids) > 0:
                    abordagens = Approach.obter_por_ids(approach_ids)
                    psicologo.approaches = abordagens
                else:
                    psicologo.approaches = []
            
            db.commit()
            db.refresh(psicologo)
            
            return psicologo
        except Exception as e:
            db.rollback()
            print(f"ERRO ao atualizar psicólogo: {e}")
            raise e
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar psicólogo"""
        db = get_db_session()
        try:
            psicologo = db.query(Psychologist).filter(Psychologist.id == self.id).first()
            if psicologo:
                db.delete(psicologo)
                db.commit()
        finally:
            db.close()
    
    @classmethod
    def buscar_com_filtros(
        cls,
        consulta: Optional[str] = None,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        ids_especialidades: Optional[List[int]] = None,
        ids_abordagens: Optional[List[int]] = None,
        consulta_online: Optional[bool] = None,
        consulta_presencial: Optional[bool] = None,
        avaliacao_minima: Optional[float] = None,
        preco_maximo: Optional[float] = None,
        experiencia_minima: Optional[int] = None,
        pagina: int = 1,
        tamanho_pagina: int = 20
    ) -> dict:
        """Buscar psicólogos com filtros"""
        from app.models.usuario import User
        
        db = get_db_session()
        try:
            # Debug: Verificar quantos psicólogos existem no total
            total_all = db.query(cls).count()
            total_verified = db.query(cls).filter(cls.esta_verificado == True).count()
            total_with_user = db.query(cls).join(User).count()
            total_with_left_join = db.query(cls).outerjoin(User).count()
            print(f"🔍 DEBUG busca_com_filtros: Total={total_all}, Verificados={total_verified}, Com User={total_with_user}, Com Left Join={total_with_left_join}")
            
            # Usar outerjoin (LEFT JOIN) para incluir psicólogos mesmo sem user associado
            # TEMPORARIAMENTE: Remover filtro is_verified para debug - retornar todos os psicólogos
            # TODO: Restaurar filtro is_verified após confirmar que os dados estão sendo retornados
            q = db.query(cls).outerjoin(User)  # Usar outerjoin em vez de join para não excluir psicólogos sem user
            print(f"🔍 DEBUG: Query inicial criada, filtros aplicados: consulta={consulta}, cidade={cidade}, estado={estado}")
            
            # Filtro por busca textual
            if consulta:
                search_term = f"%{consulta}%"
                q = q.filter(
                    or_(
                        User.nome_completo.ilike(search_term),
                        cls.biografia.ilike(search_term),
                        cls.crp.ilike(search_term)
                    )
                )
            
            # Filtro por cidade
            if cidade:
                q = q.filter(cls.cidade.ilike(f"%{cidade}%"))
            
            # Filtro por estado
            if estado:
                q = q.filter(cls.estado.ilike(f"%{estado}%"))
            
            # Filtro por especialidades
            if ids_especialidades:
                from app.models.especialidade import Specialty
                q = q.join(cls.specialties).filter(
                    Specialty.id.in_(ids_especialidades)
                )
            
            # Filtro por abordagens
            if ids_abordagens:
                from app.models.abordagem import Approach
                q = q.join(cls.approaches).filter(
                    Approach.id.in_(ids_abordagens)
                )
            
            # Aplicar distinct se houver joins com especialidades ou abordagens
            if ids_especialidades or ids_abordagens:
                q = q.distinct()
            
            # Filtro por tipo de consulta
            if consulta_online is not None:
                q = q.filter(cls.consulta_online == consulta_online)
            
            if consulta_presencial is not None:
                q = q.filter(cls.consulta_presencial == consulta_presencial)
            
            # Filtro por rating mínimo
            if avaliacao_minima is not None:
                q = q.filter(cls.avaliacao >= avaliacao_minima)
            
            # Filtro por preço máximo
            if preco_maximo is not None:
                q = q.filter(
                    or_(
                        cls.preco_consulta <= preco_maximo,
                        cls.preco_consulta.is_(None)
                    )
                )
            
            # Filtro por experiência mínima
            if experiencia_minima is not None:
                q = q.filter(cls.anos_experiencia >= experiencia_minima)
            
            # Contar total (usar distinct se necessário)
            if ids_especialidades or ids_abordagens:
                total = q.distinct().count()
            else:
                total = q.count()
            
            print(f"🔍 DEBUG: Total após filtros={total}, Página={pagina}, Tamanho={tamanho_pagina}")
            
            # Paginação
            skip = (pagina - 1) * tamanho_pagina
            psychologists = q.options(
                joinedload(cls.user),
                joinedload(cls.specialties),
                joinedload(cls.approaches)
            ).order_by(
                cls.avaliacao.desc(),
                cls.total_avaliacoes.desc()
            ).offset(skip).limit(tamanho_pagina).all()
            
            print(f"🔍 DEBUG: Psicólogos retornados={len(psychologists)}")
            if psychologists:
                print(f"🔍 DEBUG: Primeiro psicólogo: id={psychologists[0].id}, id_usuario={psychologists[0].id_usuario}, esta_verificado={psychologists[0].esta_verificado}")
                if psychologists[0].user:
                    print(f"🔍 DEBUG: User do primeiro: id={psychologists[0].user.id}, name={psychologists[0].user.nome_completo}")
                else:
                    print(f"⚠️ DEBUG: Primeiro psicólogo não tem user associado!")
            
            return {
                "psychologists": psychologists,
                "total": total,
                "page": pagina,
                "page_size": tamanho_pagina
            }
        finally:
            db.close()
    
    @classmethod
    def buscar_para_mapa(
        cls,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        id_especialidade: Optional[int] = None,
        id_abordagem: Optional[int] = None
    ) -> List["Psychologist"]:
        """Buscar psicólogos para mapa interativo"""
        from app.models.especialidade import Specialty
        from app.models.abordagem import Approach
        
        db = get_db_session()
        try:
            query = db.query(cls).options(
                joinedload(cls.user),
                joinedload(cls.specialties),
                joinedload(cls.approaches)
            ).filter(cls.esta_verificado == True)
            
            # Filtros
            if cidade:
                query = query.filter(cls.cidade.ilike(f"%{cidade}%"))
            
            if estado:
                query = query.filter(cls.estado.ilike(f"%{estado}%"))
            
            if id_especialidade:
                query = query.join(cls.specialties).filter(
                    Specialty.id == id_especialidade
                )
            
            if id_abordagem:
                query = query.join(cls.approaches).filter(
                    Approach.id == id_abordagem
                )
            
            return query.all()
        finally:
            db.close()

