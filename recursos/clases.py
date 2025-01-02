import gurobipy as gp
from gurobipy import GRB
from typing import List, Dict, Any

class Vehiculo:
    """
    Clase que representa un vehículo con identificador, capacidad de carga, 
    carga actual y posición en un sistema 1D.
    """
    def __init__(self, identif, capacidad, carga=0, posicion=0):
        """
        Inicializa una nueva instancia de Vehiculo.

        Args:
            identif (str): Identificador único del vehículo.
            capacidad (int): Capacidad máxima de carga del vehículo.
            carga (int, opcional): Carga actual del vehículo. Por defecto es 0.
            posicion (int, opcional): Posición actual del vehículo en un sistema 1D. Por defecto es 0.
        """
        self.identif = identif
        self.capacidad = capacidad
        self.carga = carga
        self.posicion = posicion

    def set_carga(self, carga):
        """
        Actualiza la carga del vehículo, validando que no supere la capacidad máxima.

        Args:
            carga (int): Nueva carga a establecer.

        Raises:
            ValueError: Si la carga supera la capacidad del vehículo.
        """
        if carga <= self.capacidad:
            self.carga = carga
        else:
            raise ValueError(f"Error: la carga ({carga}) supera la capacidad máxima ({self.capacidad}).")

    def set_posicion(self, posicion):
        """
        Actualiza la posición del vehículo.

        Args:
            posicion (int): Nueva posición a establecer.
        """
        self.posicion = posicion

    def get_carga(self):
        """
        Devuelve la carga actual del vehículo.

        Returns:
            int: Carga actual.
        """
        return self.carga

    def get_posicion(self):
        """
        Devuelve la posición actual del vehículo.

        Returns:
            int: Posición actual.
        """
        return self.posicion

    def __str__(self):
        """
        Devuelve una representación en cadena del estado del vehículo.

        Returns:
            str: Estado del vehículo en formato legible.
        """
        return (f"Vehículo ID: {self.identif}\n"
                f"Capacidad: {self.capacidad}\n"
                f"Carga Actual: {self.carga}\n"
                f"Posición Actual: {self.posicion}")

class Destino:
    """
    Clase que representa un destino con inventario, consumo promedio y planificación 
    de tiempo de cobertura.
    """
    def __init__(self, identif, consumo_promedio, tiempo_cobertura_plan, inventario=0):
        """
        Inicializa una nueva instancia de Destino.

        Args:
            identif (str): Identificador único del destino.
            consumo_promedio (float): Consumo promedio por unidad de tiempo.
            tiempo_cobertura_plan (float): Tiempo planificado de cobertura en unidades de tiempo.
            inventario (float, opcional): Cantidad inicial de inventario. Por defecto es 0.

        Raises:
            ValueError: Si `consumo_promedio` o `tiempo_cobertura_plan` son menores o iguales a cero.
        """
        if consumo_promedio <= 0:
            raise ValueError("El consumo promedio debe ser mayor a cero.")
        if tiempo_cobertura_plan <= 0:
            raise ValueError("El tiempo de cobertura planificado debe ser mayor a cero.")
        
        self.identif = identif
        self.consumo_promedio = consumo_promedio
        self.tiempo_cobertura_plan = tiempo_cobertura_plan
        self.inventario = inventario
        
        # Cálculos iniciales
        self.tiempo_cobertura = self._calcular_tiempo_cobertura()
        self.demanda = self._calcular_demanda()

    def _calcular_tiempo_cobertura(self):
        """
        Calcula el tiempo de cobertura en función del inventario y el consumo promedio.

        Returns:
            float: Tiempo de cobertura actual.

        Raises:
            ValueError: Si el consumo promedio es cero (para evitar división por cero).
        """
        if self.consumo_promedio == 0:
            raise ValueError("El consumo promedio no puede ser cero.")
        return self.inventario / self.consumo_promedio

    def _calcular_demanda(self):
        """
        Calcula la demanda en función del consumo promedio, tiempo planificado y el inventario.

        Returns:
            float: Demanda actual.
        """
        return self.consumo_promedio * self.tiempo_cobertura_plan - self.inventario

    def set_inventario(self, carga):
        """
        Actualiza el inventario y recalcula los valores dependientes.

        Args:
            inventario (float): Nuevo valor del inventario.

        Raises:
            ValueError: Si el inventario es negativo.
        """
        if carga < 0:
            raise ValueError("El inventario no puede ser negativo.")
        
        self.inventario += carga
        self.tiempo_cobertura = self._calcular_tiempo_cobertura()
        self.demanda = self._calcular_demanda()

    def get_inventario(self):
        """
        Devuelve el inventario actual.

        Returns:
            float: Inventario actual.
        """
        return self.inventario

    def get_tiempo_cobertura(self):
        """
        Devuelve el tiempo de cobertura actual.

        Returns:
            float: Tiempo de cobertura actual.
        """
        return self.tiempo_cobertura

    def get_demanda(self):
        """
        Devuelve la demanda actual.

        Returns:
            float: Demanda actual.
        """
        return self.demanda

    def __str__(self):
        """
        Devuelve una representación en cadena del estado del destino.

        Returns:
            str: Estado del destino en formato legible.
        """
        return (f"Destino ID: {self.identif}\n"
                f"Consumo Promedio: {self.consumo_promedio}\n"
                f"Tiempo de Cobertura Planificado: {self.tiempo_cobertura_plan}\n"
                f"Inventario Actual: {self.inventario}\n"
                f"Tiempo de Cobertura Actual: {self.tiempo_cobertura:.2f}\n"
                f"Demanda Actual: {self.demanda:.2f}")

class ModeloOpt:
    """
    Clase para representar un modelo de optimización de distribución de vehículos a destinos.

    Atributos:
        name_model (str): Nombre del modelo.
        list_vehiculos (List[Any]): Lista de vehículos, cada uno con un identificador único.
        list_destinos (List[Any]): Lista de destinos, cada uno con un identificador único.
        params_FO (Dict[tuple, float]): Parámetros de la función objetivo, donde la clave es una tupla (vehículo, destino).
    """

    def __init__(self, name_model: str, list_vehiculos: List[Any], list_destinos: List[Any], params_FO: Dict[tuple, float],params_carga: Dict[tuple, float]):
        self.name_model = name_model
        self.list_vehiculos = list_vehiculos
        self.list_destinos = list_destinos
        self.params_FO = params_FO
        self.params_carga = params_carga
        self.plan_distribution = {}
        self.ind_traf_opt = None

    def build_model(self) -> gp.Model:
        """
        Construye el modelo de optimización utilizando Gurobi.

        Returns:
            gp.Model: El modelo Gurobi configurado.
        """
        # Crear modelo de Gurobi
        model = gp.Model(self.name_model)

        # Extraer identificadores de vehículos y destinos
        self.vehiculos_id = [veh.identif for veh in self.list_vehiculos]
        self.destinos_id = [destino.identif for destino in self.list_destinos]

        # Variables de decisión: Asignación binaria de vehículos a destinos
        self.assign = model.addVars(
            self.vehiculos_id, self.destinos_id,
            vtype=GRB.BINARY,
            name="Asignacion"
        )

        # Restricción: Cada destino debe ser asignado exactamente a un vehículo
        model.addConstrs(
            (gp.quicksum(self.assign[(i, j)] for i in self.vehiculos_id) == 1 for j in self.destinos_id),
            name="Rest_vehXdestino"
        )

        # Restricción: Cada vehículo debe ser asignado exactamente a un destino
        model.addConstrs(
            (gp.quicksum(self.assign[(i, j)] for j in self.destinos_id) == 1 for i in self.vehiculos_id),
            name="Rest_destinoXveh"
        )

        # Función objetivo: Maximizar la utilidad según los parámetros dados
        funcion_objetivo = gp.quicksum(
            self.assign[(i, j)] * self.params_FO[(i, j)]
            for i in self.vehiculos_id
            for j in self.destinos_id
        )
        model.setObjective(funcion_objetivo, GRB.MAXIMIZE)

        return model

    def solve(self) -> Dict[str, Any]:
        """
        Resuelve el modelo de optimización y devuelve los resultados.

        Returns:
            Dict[str, Any]: Diccionario con los resultados de la optimización.
        """
        # Construir el modelo
        model = self.build_model()
        if len(self.list_destinos)==1:
            diccionario = self.params_FO
            plan_max_trafico = max(diccionario, key=diccionario.get)
            vehiculo_id,destino_id=plan_max_trafico
            carga_entregada = self.params_carga[plan_max_trafico]
            self.plan_distribution = {plan_max_trafico:1.0}
            results = {
                    "Etapa": self.name_model,
                    "Ruteo": self.plan_distribution,
                    "Val_Obj_opt": self.params_FO[plan_max_trafico]
            }
            with open('results/resultado.csv','a') as file:
                file.write(f'\n{self.name_model},')
                file.write(f'{vehiculo_id},')
                file.write(f'{destino_id},') 
                file.write(f'{carga_entregada}')
            return results
        else:
            try:
                # Optimizar el modelo
                model.optimize()
    
                # Verificar si se encontró una solución óptima
                if model.Status == GRB.OPTIMAL:
                    # Extraer el plan de distribución y el valor de la función objetivo
                    self.plan_distribution = {
                        (i, j): self.assign[i, j].X
                        for i in self.vehiculos_id
                        for j in self.destinos_id
                    }
                    self.ind_traf_opt = model.ObjVal
    
                    # Devolver resultados en un formato claro
                    results = {
                        "Etapa": self.name_model,
                        "Ruteo": self.plan_distribution,
                        "Val_Obj_opt": self.ind_traf_opt
                    }
                    with open(results/'resultado.csv','a') as file:
                        for i in self.vehiculos_id:
                            for j in self.destinos_id:
                                if self.assign[i, j].X==1:
                                    file.write(f'\n{self.name_model},')
                                    file.write(f'{i},')
                                    file.write(f'{j},')
                                    file.write(f'{self.params_carga[(i,j)]}')
                    return results
                else:
                    raise ValueError(f"El modelo no encontró una solución óptima. Status: {model.Status}")
    
            except gp.GurobiError as e:
                raise RuntimeError(f"Error en Gurobi: {e.message}")
            except Exception as e:
                raise RuntimeError(f"Error inesperado: {str(e)}")
